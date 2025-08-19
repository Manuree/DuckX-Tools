import bpy
import bmesh

def flip_uv(x=True):
    """
    Flip UVs จากหน้า View 3D ได้โดยตรง
    x=True  -> Flip ตามแกน X (U)
    x=False -> Flip ตามแกน Y (V)

    ลำดับการทำงานใน Edit Mode:
      1) ถ้ามี FACE ถูกเลือก -> กลับทุก UV loop ของ faces ที่ถูกเลือก (ไม่สน UV selection)
      2) ถ้าไม่มี FACE ถูกเลือกแต่มี UV ถูกเลือก -> กลับเฉพาะ UV ที่ถูกเลือก
      3) ถ้าไม่ทั้งสองอย่าง -> กลับทั้ง mesh
    ใน Object Mode: ทำกับวัตถุ mesh ที่เลือกทั้งหมด
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

        faces_sel = [f for f in bm.faces if f.select]
        if faces_sel:
            # กรณีมี FACE ถูกเลือก: ทำทุก loop ใน faces เหล่านี้
            for f in faces_sel:
                for loop in f.loops:
                    luv = loop[uv_layer]
                    uv = luv.uv
                    uv[axis] = 1.0 - uv[axis]
        else:
            # ไม่มี FACE ถูกเลือก -> ตรวจ UV selection
            any_uv_selected = any(loop[uv_layer].select for f in bm.faces for loop in f.loops)
            if any_uv_selected:
                for f in bm.faces:
                    for loop in f.loops:
                        luv = loop[uv_layer]
                        if luv.select:
                            uv = luv.uv
                            uv[axis] = 1.0 - uv[axis]
            else:
                # ไม่มีทั้ง FACE และ UV selection -> ทำทั้ง mesh
                for f in bm.faces:
                    for loop in f.loops:
                        luv = loop[uv_layer]
                        uv = luv.uv
                        uv[axis] = 1.0 - uv[axis]

        bmesh.update_edit_mesh(me, loop_triangles=False, destructive=False)

    else:
        # Object Mode: ทำกับวัตถุ mesh ที่เลือกทั้งหมด (ถ้าไม่มีก็ทำกับ active)
        targets = [o for o in (ctx.selected_objects or []) if o.type == 'MESH'] or [obj]
        for ob in targets:
            me = ob.data
            uv_act = me.uv_layers.active
            if not uv_act:
                continue
            # เดินตาม loop index เพื่อครอบคลุมทุกหน้า
            for li in me.loops:
                uv = uv_act.data[li.index].uv
                uv[axis] = 1.0 - uv[axis]
            me.update()
