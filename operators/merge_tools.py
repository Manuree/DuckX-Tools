import bpy
import bmesh
from bpy.types import (Operator)
from bpy.props import (EnumProperty, PointerProperty, StringProperty, FloatVectorProperty, FloatProperty, IntProperty, BoolProperty)

from . import func_core

class Duckx_OT_MergeBySize(Operator):
    bl_idname = "duckx_tools.merge_by_size"
    bl_label = "Merge By Size"
    bl_icon = "LIGHTPROBE_PLANAR"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Merge By Size"

    action : StringProperty(name="Action")  
    size : FloatProperty(name="Factor", min=0, step=0.0001, precision=6)
    offset : FloatProperty(name="Offset", step=0.001, precision=6)
    KeepSize : BoolProperty(name="Keep Size")

    def execute(self, context):
        obj = bpy.context.active_object
        for modifier in obj.modifiers:
            print(modifier.type)
            if modifier.type == "WEIGHTED_NORMAL":
                print("WEIGHTED_NORMAL: ")
                bpy.context.object.modifiers["WeightedNormal"].show_viewport = False     
        
        if self.action == "face":
            self.face(self, context)
        elif self.action == "edge":
            self.edge(self, context)
            
        for modifier in obj.modifiers:
            print(modifier.type)
            if modifier.type == "WEIGHTED_NORMAL":
                print("WEIGHTED_NORMAL: ")
                bpy.context.object.modifiers["WeightedNormal"].show_viewport = True
        return {'FINISHED'}
    @staticmethod
    def face(self, context):
        obj = bpy.context.active_object
        if obj and obj.type == 'MESH' and bpy.context.mode == 'EDIT_MESH':
            #bpy.ops.mesh.select_all(action='DESELECT')
            try:
                bpy.ops.object.vertex_group_set_active(group='MergeBySize_face')
                bpy.ops.object.vertex_group_remove()
                bpy.ops.object.vertex_group_set_active(group='MergeBySize_vert')
                bpy.ops.object.vertex_group_remove()
                print("Remove Vertex Group")
            except:
                print("Vertex Group Clean")
            bpy.context.object.vertex_groups.new(name='MergeBySize_face')
            bpy.ops.object.vertex_group_assign()
            bpy.context.object.vertex_groups.new(name='MergeBySize_vert')

            bm = bmesh.from_edit_mesh(obj.data)

            for face in bm.faces:
                #print(face)
                bpy.ops.object.vertex_group_set_active(group='MergeBySize_face')
                bpy.ops.object.vertex_group_select()
                area = face.calc_area()
                if face.select:
                    if area < self.size:
                        print(area)
                        bpy.ops.mesh.select_all(action='DESELECT')
                        bpy.ops.mesh.select_mode(type='FACE')
                        a_face = face
                        face.select_set(True)
                        if self.KeepSize:
                            bpy.ops.transform.shrink_fatten(value=func_core.edge_length()/2 * 1.64085355 + self.offset)
                        else:
                            bpy.ops.transform.shrink_fatten(value=self.offset)
                        bpy.ops.object.vertex_group_set_active(group='MergeBySize_vert')
                        bpy.ops.object.vertex_group_assign()
                        bpy.ops.duckx_tools.utilities_operator(action="Scale 0")
            # Update the BMesh back to the mesh data
            bmesh.update_edit_mesh(obj.data)

            # Free the BMesh
            bm.free()
            
            bpy.ops.object.vertex_group_set_active(group='MergeBySize_vert')
            bpy.ops.object.vertex_group_select()
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
            bpy.ops.mesh.mark_sharp()
        try:
            bpy.ops.object.vertex_group_set_active(group='MergeBySize_face')
            bpy.ops.object.vertex_group_remove()
            bpy.ops.object.vertex_group_set_active(group='MergeBySize_vert')
            bpy.ops.object.vertex_group_remove()
            print("Remove Vertex Group")
        except:
            print("Vertex Group Clean")
        #bpy.ops.screen.redo_last('INVOKE_DEFAULT')
        #bpy.ops.screen.redo_last('INVOKE_REGION_WIN')
        return {'FINISHED'}
    @staticmethod
    def edge(self, context):
        obj = bpy.context.active_object
        if obj and obj.type == 'MESH' and bpy.context.mode == 'EDIT_MESH':
            try:
                obj = bpy.context.active_object
                bm = bmesh.from_edit_mesh(obj.data)
                edge_selected = []
                for edge in bm.edges:
                    if edge.select:
                        if edge.calc_length() < self.size*200:
                            edge_selected.append(edge)
                print(edge_selected)
                bpy.ops.mesh.select_all(action='DESELECT')
                for edge in edge_selected:
                    edge.select_set(True)
                    bpy.ops.duckx_tools.utilities_operator(action="Scale 0")
            except:
                print("Edge Length Error")

        return {'FINISHED'}
    
def register():
    bpy.utils.register_class(Duckx_OT_MergeBySize)
        
    
def unregister():
    bpy.utils.unregister_class(Duckx_OT_MergeBySize)
        