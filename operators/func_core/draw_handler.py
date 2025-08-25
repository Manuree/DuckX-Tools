import bpy
import gpu
from gpu_extras.batch import batch_for_shader

# ---------- Module State ----------
_handle = None
_color = (0.0, 1.0, 0.0, 1.0)  # RGBA
_thickness = 2.0               # px
_margin = 8                    # px

# ชื่อ key สำหรับเก็บรีจิสทรี handler ข้ามการ reload
_REG_KEY = "DuckX_DrawHandles_Registry"

# ใช้ชื่อ shader แบบใหม่ใน 4.4
_shader = gpu.shader.from_builtin("UNIFORM_COLOR")


def _get_registry():
    """
    คืนชุด (set) ของ handler ที่เก็บไว้ใน bpy.app.driver_namespace
    ข้อดี: อยู่ข้ามการ reload โมดูล, ลบรวดเดียวได้
    """
    ns = bpy.app.driver_namespace
    reg = ns.get(_REG_KEY)
    if reg is None:
        reg = set()
        ns[_REG_KEY] = reg
    return reg


def _draw_callback():
    region = bpy.context.region
    if region is None:
        return

    w, h = region.width, region.height
    if w <= 0 or h <= 0:
        return

    x0 = _margin
    y0 = _margin
    x1 = w - _margin
    y1 = h - _margin

    # วาดด้วย primitive "LINES" -> 4 ด้าน (2 จุดต่อเส้น)
    verts = [
        (x0, y0), (x1, y0),  # bottom
        (x1, y0), (x1, y1),  # right
        (x1, y1), (x0, y1),  # top
        (x0, y1), (x0, y0),  # left
    ]

    batch = batch_for_shader(_shader, "LINES", {"pos": verts})

    gpu.state.blend_set("ALPHA")
    gpu.state.line_width_set(float(_thickness))

    _shader.bind()
    _shader.uniform_float("color", _color)
    batch.draw(_shader)

    # reset กัน state ค้าง
    gpu.state.line_width_set(1.0)
    gpu.state.blend_set("NONE")


# ---------- Public API ----------
def draw_handler_start(color=(0.0, 1.0, 0.0, 1.0), thickness=2.0, margin=8):
    """เริ่มวาดกรอบบนทุก View 3D"""
    global _handle, _color, _thickness, _margin
    _color = tuple(color)
    _thickness = float(thickness)
    _margin = int(margin)

    if _handle is None:
        _handle = bpy.types.SpaceView3D.draw_handler_add(
            _draw_callback, (), "WINDOW", "POST_PIXEL"
        )
        # เก็บลงรีจิสทรี (สำคัญมากสำหรับ clear ข้าม reload)
        _get_registry().add(_handle)
        _tag_redraw_all_3dview()


def draw_handler_stop():
    """หยุดวาดกรอบ (เฉพาะ handler ปัจจุบันของโมดูลนี้)"""
    global _handle
    if _handle is not None:
        try:
            bpy.types.SpaceView3D.draw_handler_remove(_handle, "WINDOW")
        except Exception:
            # ถ้าถอดซ้ำ/ไม่พบ ก็ปล่อยผ่าน
            pass
        # ลบออกจากรีจิสทรีด้วย
        _get_registry().discard(_handle)
        _handle = None
        _tag_redraw_all_3dview()


def draw_handler_toggle(color=None, thickness=None, margin=None):
    """สลับเปิด/ปิด (ถ้าจะเปิดใหม่ ใช้พารามิเตอร์ที่ส่งมา หรือค่าเดิม)"""
    if draw_handler_is_running():
        draw_handler_stop()
    else:
        c = color if color is not None else _color
        t = thickness if thickness is not None else _thickness
        m = margin if margin is not None else _margin
        draw_handler_start(c, t, m)


def draw_handler_update(color=None, thickness=None, margin=None):
    """อัปเดตพารามิเตอร์ระหว่างที่กำลังวาดอยู่"""
    global _color, _thickness, _margin
    if color is not None:
        _color = tuple(color)
    if thickness is not None:
        _thickness = float(thickness)
    if margin is not None:
        _margin = int(margin)
    if draw_handler_is_running():
        _tag_redraw_all_3dview()


def draw_handler_is_running():
    return _handle is not None


def draw_handler_clear_all():
    """
    ล้าง overlay ทั้งหมดที่โมดูล/แอดออนนี้เคยสร้างไว้ (ข้ามรอบ reload):
    - ถอดทุก handler ที่เคยบันทึกในรีจิสทรี
    - รีเซ็ต state ที่จำเป็น
    - บังคับ redraw ทุก View 3D
    คืนค่าจำนวน handler ที่ถูกถอด
    """
    removed = 0

    # ไล่ถอดทุก handler ที่เคยเก็บไว้ (รวมตัวเก่าจากรอบ reload ด้วย)
    reg = _get_registry()
    for h in list(reg):
        try:
            bpy.types.SpaceView3D.draw_handler_remove(h, "WINDOW")
            removed += 1
        except Exception:
            # บางตัวอาจถอดไปแล้ว หรือ invalid; ข้าม
            pass
        finally:
            reg.discard(h)

    # กันกรณี _handle ปัจจุบันยังอยู่
    global _handle
    if _handle is not None:
        try:
            bpy.types.SpaceView3D.draw_handler_remove(_handle, "WINDOW")
            removed += 1
        except Exception:
            pass
        _handle = None

    # รีเซ็ต state และบังคับ redraw
    try:
        gpu.state.line_width_set(1.0)
        gpu.state.blend_set("NONE")
    except Exception:
        pass

    _tag_redraw_all_3dview()
    return removed


# ---------- Utilities ----------
def _tag_redraw_all_3dview():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == "VIEW_3D":
                for region in area.regions:
                    if region.type == "WINDOW":
                        region.tag_redraw()
