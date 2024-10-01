import bmesh
import bpy
import random
import math
from mathutils import Vector
from bpy.types import (Context, Event, Operator)
from bpy.props import (EnumProperty, PointerProperty, StringProperty, FloatVectorProperty, FloatProperty, IntProperty, BoolProperty)
from . import func_core

  
class Duckx_OT_DecalRing(Operator):
    bl_idname = "duckx_tools.decal_ring_operator"
    bl_label = "Ring Decal"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Ring shape decal"

    decalAxis : EnumProperty(name="Axis", items=[("X", "X", "", "SEQUENCE_COLOR_01", 1), ("Y", "Y", "", "SEQUENCE_COLOR_04", 2), ("Z", "Z", "", "SEQUENCE_COLOR_05", 3)])
    orient : IntProperty(name="Orient Index", default=0, min=0)
    offset : FloatProperty(name="Offset", default=0.002, precision=5, step=0.0010)
    height : FloatProperty(name="Height", default=0.126)
    uv_position : FloatVectorProperty(name="UV Position : ", subtype="XYZ")
    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH' and context.tool_settings.mesh_select_mode[2]
    
    def invoke(self, context, event):
        self.orient = 0
        return self.execute(context)
        # print(self.orient)
        # if event.shift:
        #     self.hide_all = False
        #     return self.execute(context)
        # else:
        #     return self.execute(context)
    def draw(self, context):
        scene = context.scene
        duckx_tools = scene.duckx_tools
        layout = self.layout
        layout.use_property_split = True
        layout.prop(self, "decalAxis", expand=True)
        layout.prop(self, "orient")
        layout.prop(self, "offset")
        layout.prop(self, "height")
        layout.prop(self, "uv_position")
        layout.prop(duckx_tools, "decal_ring_mat", text="Material")
        
    def execute(self, context):
        scene = context.scene
        duckx_tools = scene.duckx_tools
        bpy.ops.wm.tool_set_by_id(name="builtin.move")
        if self.decalAxis == "Y":
            decalStart = (0, -self.height*0.5, 0)
            decalEnd = (0, self.height, 0)
        elif self.decalAxis == "X":
            decalStart = (-self.height*0.5, 0, 0)
            decalEnd = (self.height, 0, 0)   
        elif self.decalAxis == "Z":
            decalStart = (0, 0, -self.height*0.5)
            decalEnd = (0, 0, self.height)

        obj = context.edit_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        bm.faces.ensure_lookup_table()
        
        print("Find material index")
        material = duckx_tools.decal_ring_mat
        ob = bpy.context.active_object
        mat=False
        if material is not None:
            for i, slot in enumerate(ob.material_slots):
                if slot.material == material:
                    print("Index Match")
                    ob.active_material_index = i
                    mat=True
                    break
            if mat==False:
                print("Add material to slot and assign to object")
                ob.data.materials.append(material)
                ob.active_material_index = i+1
        else:
            print("Material not found")
            self.report({"INFO"} ,"Material not found")
        bpy.ops.object.material_slot_assign()

        faces_a = []
        for face in bm.faces:
            if face.select:
                faces_a.append(face)

        #Find Oreint
        bpy.ops.mesh.select_more()
        
        face_data = []
        for face in bm.faces:
            if face.select:
                area = face.calc_area()
                face_data.append([face, area])
        face_data = sorted(face_data, key=lambda x: x[1], reverse=True)
        bpy.ops.mesh.select_all(action='DESELECT')
        for index in range(len(face_data)):
            if self.orient < len(face_data):
                if index ==  self.orient:
                    print(face_data[index])
                    face_data[index][0].select = True
            else:
                face_data[0][0].select = True    
             
        #func_core.select_face_by_size("L")
        bpy.ops.duckx_tools.orienselect_operator()
        bpy.ops.mesh.select_all(action='DESELECT')

        for face in faces_a:
            face.select = True
        
        #Create Ring
        bpy.ops.mesh.duplicate_move(MESH_OT_duplicate={"mode":1}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_type":'GLOBAL', "orient_matrix":((0, 0, 0), (0, 0, 0), (0, 0, 0)), "orient_matrix_type":'GLOBAL'})
        bpy.ops.transform.translate(value=(decalStart), orient_type='Face')
        
        faces_a.clear()
        for face in bm.faces:
            if face.select:
                faces_a.append(face)
        
        bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":(decalEnd), "orient_type":'Face',})
        bpy.ops.mesh.delete(type='FACE')

        for face in faces_a:
            face.select = True
        
        bpy.ops.duckx_tools.invert_in_loose_parts_operator()
        bpy.ops.mesh.duplicate_move(MESH_OT_duplicate={"mode":1}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_type":'GLOBAL', "orient_matrix":((0, 0, 0), (0, 0, 0), (0, 0, 0)), "orient_matrix_type":'GLOBAL'})
        
        faces_b = []
        for face in bm.faces:
            if face.select:
                faces_b.append(face)
        
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.transform.shrink_fatten(value=self.offset, use_even_offset=True, mirror=True)
        bpy.ops.mesh.select_all(action='DESELECT')

        for face in faces_a:
            face.select = True
       
        bpy.ops.mesh.select_linked(delimit={'NORMAL'})
        bpy.ops.mesh.select_more()
        bpy.ops.mesh.select_linked(delimit={'NORMAL'})
        bpy.ops.mesh.select_more()
        bpy.ops.mesh.select_linked(delimit={'NORMAL'})
        bpy.ops.mesh.select_more()
        bpy.ops.mesh.delete(type='FACE')

        # for face in faces_b:
        #     face.select = True

        #Mark Seam
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
        
        seam_found = False
        for face in faces_b:
            for edge in face.edges:
                if len(edge.link_faces) == 2:
                    edge.seam  = True
                    seam_found = True
                    break
            if seam_found:
                break  

        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
        for face in faces_b:
            face.select = True

        #Unwarp UV
        bpy.ops.uv.unwrap(method='ANGLE_BASED')

        bmesh.update_edit_mesh(me)


        return {'FINISHED'}
    
def register():
    bpy.utils.register_class(Duckx_OT_DecalRing)

        
    
def unregister():
    bpy.utils.unregister_class(Duckx_OT_DecalRing)

