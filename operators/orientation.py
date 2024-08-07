import bpy
import bmesh
from bpy.types import (Operator)

class Duckx_OT_OrientSelect(Operator):
    bl_idname = "duckx_tools.orienselect_operator"
    bl_label = "Selection"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_description = "Orientation Face for Decal alignment and axis"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        if bpy.context.mode == 'EDIT_MESH':
            types = ["Face", "Edge", "Vertex"]
            for type in types:
                try:
                    bpy.context.scene.transform_orientation_slots[0].type = type
                    bpy.ops.transform.delete_orientation()
                except:
                    bpy.context.scene.transform_orientation_slots[0].type = 'GLOBAL'
            bpy.ops.transform.create_orientation(use=True)
            bpy.context.scene.tool_settings.transform_pivot_point = 'BOUNDING_BOX_CENTER'
            
            bpy.ops.wm.tool_set_by_id(name="builtin.move")
            bpy.context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'
        elif bpy.context.mode == 'OBJECT':
            bpy.context.scene.transform_orientation_slots[0].type = 'LOCAL'

        return {'FINISHED'}
    
class Duckx_OT_OrientGlobal(Operator):
    bl_idname = "duckx_tools.orienglobal_operator"
    bl_label = "Global"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_icon = "ORIENTATION_GLOBAL"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Back to orientation Global and remove Face orientation"

    def execute(self, context):
        pivot_point = bpy.context.scene.tool_settings.transform_pivot_point
        types = ["Face", "Edge", "Vertex"]
        for type in types:
            try:
                bpy.context.scene.transform_orientation_slots[0].type = type
                bpy.ops.transform.delete_orientation()
            except:
                bpy.context.scene.transform_orientation_slots[0].type = 'GLOBAL'
        bpy.context.scene.transform_orientation_slots[0].type = 'GLOBAL'
        bpy.context.scene.tool_settings.transform_pivot_point = pivot_point

        return {'FINISHED'}
    
class Duckx_OT_OrientAndPivot(Operator):
    bl_idname = "duckx_tools.orien_and_pivot_operator"
    bl_label = "Orient And Pivot"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_icon = "ORIENTATION_GLOBAL"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Orientation and Pivot to 3D Cursor"

    def execute(self, context):
        obj = bpy.context.active_object
        bm = bmesh.from_edit_mesh(obj.data)
        edge_selected = []
        edge_active = None
        for edge in bm.edges:
            if edge.select:
                edge_selected.append(edge)
        bpy.ops.mesh.select_prev_item()
        bpy.ops.mesh.select_all(action='INVERT')
        for edge in bm.edges:
            if edge.select:
                if edge in edge_selected:
                    edge_active = edge
        bpy.ops.mesh.select_all(action='DESELECT')
        edge_active.select_set(True)
        bpy.ops.duckx_tools.orienselect_operator()
        bpy.ops.view3d.snap_cursor_to_selected()
        bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'
        bpy.context.scene.tool_settings.use_transform_correct_face_attributes = False
        bpy.ops.mesh.select_all(action='DESELECT')
        edge_selected.remove(edge_active)
        for edge in edge_selected:
            edge.select_set(True)

        return {'FINISHED'}
    
    
def register():
    bpy.utils.register_class(Duckx_OT_OrientSelect)
    bpy.utils.register_class(Duckx_OT_OrientGlobal)
    bpy.utils.register_class(Duckx_OT_OrientAndPivot)
        
    
def unregister():
    bpy.utils.unregister_class(Duckx_OT_OrientSelect)
    bpy.utils.unregister_class(Duckx_OT_OrientGlobal)
    bpy.utils.unregister_class(Duckx_OT_OrientAndPivot)
        
