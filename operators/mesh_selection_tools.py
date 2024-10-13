import bpy

from . import func_core

from bpy.types import (Operator )
from bpy.props import (EnumProperty, PointerProperty, StringProperty, FloatVectorProperty, FloatProperty, IntProperty, BoolProperty)

class Duckx_OT_SelectFromIndex(Operator):
    bl_idname = "duckx_tools.select_from_index_operator"
    bl_label = "Select From Index"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_icon = "EMPTY_ARROWS"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Select From Index"

    action : StringProperty(name="Action")

    def execute(self, context):
        scene = context.scene
        duckx_tools = scene.duckx_tools
        action = duckx_tools.select_type
        obj = bpy.context.active_object
        
        bpy.ops.wm.tool_set_by_id(name="builtin.move")
        if action == "vertex":
            bpy.ops.mesh.select_mode(type='FACE')
            func_core.select_vertex_by_index(obj, duckx_tools.select_index_number)
        elif action == "edge":
            bpy.ops.mesh.select_mode(type='EDGE')
            func_core.select_edge_by_index(obj, duckx_tools.select_index_number)
        elif action == "face":
            bpy.ops.mesh.select_mode( type='VERT')
            func_core.select_face_by_index(obj, duckx_tools.select_index_number)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(Duckx_OT_SelectFromIndex)
        
    
def unregister():
    bpy.utils.unregister_class(Duckx_OT_SelectFromIndex)
        
