import bpy
from bpy.types import (Operator)

class Duckx_OT_AddEmpty(Operator):
    bl_idname = "duckx_tools.addempty_operator"
    bl_label = "Add Empty"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_icon = "EMPTY_ARROWS"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add Empty to center of mass"

    def execute(self, context):
        if bpy.context.mode == 'EDIT_MESH':
            editMode = True
            bpy.ops.duckx_tools.orienselect_operator()
            bpy.ops.view3d.snap_cursor_to_selected()
            bpy.ops.object.mode_set(mode='OBJECT')
        elif bpy.context.mode == 'OBJECT':
            editMode = False
            bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')
            bpy.ops.view3d.snap_cursor_to_selected()

        bpy.ops.object.empty_add(type='ARROWS', align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        bpy.ops.view3d.snap_selected_to_cursor(use_offset=True)
        bpy.ops.space_data.context = 'DATA'
        bpy.context.object.empty_display_size = 0.25
        bpy.ops.space_data.context = 'OBJECT'
       

        if editMode:
            bpy.ops.transform.transform(mode='ALIGN', orient_type="Face")
            bpy.context.object.name = "Socket_"
        else:
            bpy.context.object.name = "COM_"+bpy.context.view_layer.active_layer_collection.collection.name
        bpy.ops.duckx_tools.orienglobal_operator()
        
        return {'FINISHED'}


    
def register():
    bpy.utils.register_class(Duckx_OT_AddEmpty)
        
    
def unregister():
    bpy.utils.unregister_class(Duckx_OT_AddEmpty)
        
