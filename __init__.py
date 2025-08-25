
bl_info = {
        "name": "DuckX Tools",
        "description": "My awesome add-on.",
        "author": "Kanong Manuree",
        "version": (2, 0),
        "blender": (3, 5, 0),
        "location": "View3D",
        "warning": "", # used for warning icon and text in add-ons panel
        "wiki_url": "",
        "tracker_url": "",
        "support": "COMMUNITY",
        "category": "Object"
        }

import bpy
from bpy.app.handlers import persistent

from . import properties
from . import ui
from . import icon_reg
from .operators import func_core

from .operators import register as reg_operators
from .operators import unregister as unreg_operators


# เรียกใช้ตัวเพิ่มคีย์แมพที่คุณมีอยู่แล้ว (ซึ่งเช็คไม่ให้ซ้ำ)
@persistent
def _duckx_ensure_keymap(_):
    try:
        # ถ้า operator ของคุณอ้างอิง scene props เช่น context.scene.duckx_tools
        # ให้แน่ใจว่า PropertyGroup ถูก register แล้วก่อนจะเรียกใช้
        bpy.ops.duckx_tools.keymap_add()
    except Exception as e:
        print("[DuckX Tools] ensure keymap skipped:", e)

# ---------- helpers ----------
def _is_data_restricted():
    # ช่วง register บางที bpy.data จะเป็น _RestrictData
    return type(bpy.data).__name__ == "_RestrictData"

def _apply_overlay_settings_from_file():
    # กันเรียกในช่วง restricted
    if _is_data_restricted():
        return
    try:
        settings = func_core.read_json("setting.json") or {}
    except Exception:
        settings = {}

    # ปิด update ชั่วคราว กันยิง write ทับ
    prev_ready = getattr(properties, "_ADDON_READY", False)
    properties._ADDON_READY = False
    try:
        for scn in bpy.data.scenes:
            props = getattr(scn, "duckx_tools", None)
            if props is None:
                continue
            props.overlay_correct_face_att = bool(
                settings.get("overlay_correct_face_att", props.overlay_correct_face_att)
            )
            props.overlay_uv_rotation = bool(
                settings.get("overlay_uv_rotation", props.overlay_uv_rotation)
            )
            props.overlay_boundary_tools = bool(
                settings.get("overlay_boundary_tools", props.overlay_boundary_tools)
            )
    finally:
        properties._ADDON_READY = prev_ready

@persistent
def _duckx_apply_overlay_on_load(_):
    # เรียกเมื่อเปิดไฟล์ .blend (กรณีเปิดไฟล์ใหม่)
    _apply_overlay_settings_from_file()

def _deferred_apply():
    # เรียกครั้งเดียวหลัง register เพื่อซิงก์ไฟล์ที่เปิดอยู่ ณ ตอน enable addon
    if _is_data_restricted():
        return 0.1  # รออีกนิดแล้วลองใหม่
    _apply_overlay_settings_from_file()
    return None  # หยุด timer

def register():
     properties.register()
     ui.register()
     icon_reg.register()
     reg_operators()
     
     # ผูกโหลดตอนเปิดไฟล์
     if _duckx_apply_overlay_on_load not in bpy.app.handlers.load_post:
          bpy.app.handlers.load_post.append(_duckx_apply_overlay_on_load)

     # 2) โหลดค่าหนึ่งรอบสำหรับไฟล์ที่เปิดอยู่ตอนนี้
     bpy.app.timers.register(_deferred_apply, first_interval=0.1)

     settings = func_core.read_json("setting.json")
     if settings.get("Keymap Assign", False):
          # ผูก handler ครั้งเดียว
          if _duckx_ensure_keymap not in bpy.app.handlers.load_post:
               bpy.app.handlers.load_post.append(_duckx_ensure_keymap)

          # (ทางเลือก) เรียกทันทีตอนเปิดใช้งานแอดออนด้วย
          try:
               bpy.ops.duckx_tools.keymap_add()
          except Exception as e:
               print("[DuckX Tools] initial keymap add skipped:", e)
     

def unregister():
     properties.unregister()
     ui.unregister()
     icon_reg.unregister()
     unreg_operators()


     if _duckx_apply_overlay_on_load in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_duckx_apply_overlay_on_load)

     if _duckx_ensure_keymap in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_duckx_ensure_keymap)
     

if __name__ == '__main__':
     register()
