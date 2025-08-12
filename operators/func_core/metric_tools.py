import bpy
import bmesh

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
        return None, "โปรดอยู่ใน Edit Mode และเลือก Mesh ก่อน"

    scene = context.scene
    unit = scene.unit_settings.length_unit
    bm = bmesh.from_edit_mesh(obj.data)

    try:
        sel_edges = [e for e in bm.edges if e.select]
        if not sel_edges:
            return None, "ยังไม่ได้เลือก Edge"

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

        return msg, None
    finally:
        bmesh.update_edit_mesh(obj.data, loop_triangles=False)