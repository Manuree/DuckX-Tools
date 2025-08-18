import bpy
import bmesh

def flip_uv(x=True):
    """
    Flip UVs ใน View 3D
    x=True  -> Flip ตามแกน X (U)
    x=False -> Flip ตามแกน Y (V)
    - Edit Mode: ถ้ามี UV ที่ถูก select จะทำเฉพาะที่ select; ถ้าไม่มีก็ทำตาม face ที่ select; ถ้าไม่มีเลยทำทั้ง mesh
    - Object Mode: ทำกับ Mesh objects ที่เลือกทั้งหมด
    """
    axis = 0 if x else 1
    ctx = bpy.context
    obj = ctx.active_object
    if not obj or obj.type != 'MESH':
        return

    if obj.mode == 'EDIT':
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        uv_layer = bm.loops.layers.uv.active
        if uv_layer is None:
            return

        # ตรวจว่ามี UV loop ที่ถูกเลือกอยู่ไหม
        any_uv_selected = any(loop[uv_layer].select for f in bm.faces for loop in f.loops)
        faces_sel = [f for f in bm.faces if f.select]
        faces_iter = faces_sel if faces_sel else bm.faces

        for f in faces_iter:
            for loop in f.loops:
                luv = loop[uv_layer]
                if any_uv_selected and not luv.select:
                    continue
                uv = luv.uv
                uv[axis] = 1.0 - uv[axis]

        bmesh.update_edit_mesh(me, loop_triangles=False, destructive=False)

    else:
        # Object Mode: ทำกับวัตถุ mesh ที่เลือกทั้งหมด (ถ้าไม่มีก็ทำกับ active)
        targets = [o for o in (ctx.selected_objects or []) if o.type == 'MESH']
        if not targets:
            targets = [obj]

        for ob in targets:
            me = ob.data
            if not me.uv_layers.active:
                continue
            uv_layer = me.uv_layers.active
            # เดินตาม loop index เพื่อให้ครอบคลุมทุกหน้า
            for li in me.loops:
                luv = uv_layer.data[li.index].uv
                luv[axis] = 1.0 - luv[axis]
            me.update()
