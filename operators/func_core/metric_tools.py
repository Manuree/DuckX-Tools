import bpy
import bmesh

from . import utils_tools

def _convert_to_unit(val_meters, unit):
    """แปลงจาก meters ไปตามหน่วยที่ตั้งใน scene.unit_settings.length_unit"""
    if unit == 'KILOMETERS':
        return val_meters / 1000.0
    elif unit == 'METERS':
        return val_meters
    elif unit == 'CENTIMETERS':
        return val_meters * 100.0
    elif unit == 'MILLIMETERS':
        return val_meters * 1000.0
    elif unit == 'MICROMETERS':
        return val_meters * 1_000_000.0
    elif unit == 'MILES':
        return val_meters / 1609.344
    elif unit == 'FEET':
        return val_meters / 0.3048
    elif unit == 'INCHES':
        return val_meters / 0.0254
    elif unit == 'THOU':
        return val_meters / 0.0000254
    else:
        return val_meters  # fallback
    
def unit_short(unit: str) -> str:
    """แปลงชื่อหน่วยเป็นตัวย่อ"""
    mapping = {
        'kilometers': 'km',
        'meters': 'm',
        'centimeters': 'cm',
        'millimeters': 'mm',
        'micrometers': 'µm',
        'miles': 'mi',
        'feet': 'ft',
        'inches': 'in',
        'thou': 'thou'
    }
    return mapping.get(unit.lower(), unit)

def edge_length(context):
    obj = context.active_object
    if not (obj and obj.type == 'MESH' and obj.mode == 'EDIT'):
        return None, "Please be in Edit Mode and select a mesh first."

    scene = context.scene
    unit = scene.unit_settings.length_unit
    bm = bmesh.from_edit_mesh(obj.data)

    try:
        sel_edges = [e for e in bm.edges if e.select]
        if not sel_edges:
            return None, "Please select Edge"

        mw = obj.matrix_world

        def e_len(e):
            v1 = mw @ e.verts[0].co
            v2 = mw @ e.verts[1].co
            return (v2 - v1).length

        lengths_m = [e_len(e) for e in sel_edges]  # คำนวณเป็น meters
        lengths_u = [_convert_to_unit(l, unit) for l in lengths_m]

        # หา active edge
        active_edge = None
        for elem in reversed(bm.select_history):
            if isinstance(elem, bmesh.types.BMEdge):
                active_edge = elem
                break

        active_len_u = _convert_to_unit(e_len(active_edge), unit) if active_edge else lengths_u[-1]

        msg = f"Active Edge: {active_len_u:.4f} {unit_short(unit)}"
        if len(lengths_u) > 1:
            total = sum(lengths_u)
            avg = total / len(lengths_u)
            msg += (
                f"\nSelected: {len(lengths_u)} | "
                f"\nTotal: {total:.4f} {unit_short(unit)} | "
                f"\nAverage: {avg:.4f} {unit_short(unit)}"
            )
            utils_tools.clipboard(total)
        return msg, None
    finally:
        bmesh.update_edit_mesh(obj.data, loop_triangles=False)

def distance_calculator() -> float:
    """
    คำนวณระยะห่างระหว่างจุดกำเนิด (origin) ของวัตถุ 2 ชิ้นที่ถูกเลือก
    - ตรวจสอบว่าเลือกไว้ "พอดี" 2 ชิ้น
    - ผลลัพธ์คืนเป็น float ในหน่วยตาม scene.unit_settings.length_unit
    - คัดลอกผลลัพธ์ (พร้อมหน่วย) ไปยัง func_core.clipboard()
    """
    ctx = bpy.context
    scene = ctx.scene
    unit = scene.unit_settings.length_unit or 'METERS'
    if unit == 'ADAPTIVE':
        # สำหรับการคำนวณเป็นตัวเลขเดี่ยว ให้ยึดเป็นเมตร
        unit = 'METERS'

    sel = list(ctx.selected_objects)
    if len(sel) != 2:
        raise RuntimeError("Please select exactly 2 objects.")

    obj_a, obj_b = sel

    # world-space origin positions
    p_a = obj_a.matrix_world.translation
    p_b = obj_b.matrix_world.translation

    # ระยะใน Blender Units (BU)
    dist_BU = (p_b - p_a).length

    # แปลง BU -> meters ด้วย scale_length
    scale_len = scene.unit_settings.scale_length or 1.0
    dist_m = dist_BU * scale_len

    # แปลง meters -> หน่วยที่ตั้ง
    dist_u = _convert_to_unit(dist_m, unit)

    # ส่งค่าเข้า func_core.clipboard() (พยายาม import ทั้งแบบ relative และ absolute)
    clipboard_text = f"{dist_u:.6f} {unit_short(unit)}"
    utils_tools.clipboard(dist_u)

    return float(dist_u)