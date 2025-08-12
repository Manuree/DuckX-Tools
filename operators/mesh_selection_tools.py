import bpy

from . import func_core

from bpy.types import (Operator )
from bpy.props import (EnumProperty, PointerProperty, StringProperty, FloatVectorProperty, FloatProperty, IntProperty, BoolProperty)

from ..ui import add_panel, add_expand_panel

class Duckx_OT_SelectFromIndex(Operator):
    bl_idname = "duckx_tools.select_from_index"
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
        
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.wm.tool_set_by_id(name="builtin.move")
        if action == "vertex":
            bpy.ops.mesh.select_mode(type='VERT')
            func_core.select_vertex_by_index(obj, duckx_tools.select_index_number)
        elif action == "edge":
            bpy.ops.mesh.select_mode(type='EDGE')
            func_core.select_edge_by_index(obj, duckx_tools.select_index_number)
        elif action == "face":
            bpy.ops.mesh.select_mode( type='FACE')
            func_core.select_face_by_index(obj, duckx_tools.select_index_number)

        return {'FINISHED'}

def draw_select_from_index(self, context, layout, properties):
    box = layout.box()
    col = box.column(align=True)
    col.label(text="Index")
    row = col.row(align=True)
    row.prop(properties, "select_type", expand=True)
    col.prop(properties, "select_index_number")
    row = box.row(align=True)
    row.scale_y = 1.5
    row.operator("duckx_tools.select_from_index", text="Select")

add_expand_panel("Selection", draw_select_from_index)

def register():
    bpy.utils.register_class(Duckx_OT_SelectFromIndex)
        
    
def unregister():
    bpy.utils.unregister_class(Duckx_OT_SelectFromIndex)
        
