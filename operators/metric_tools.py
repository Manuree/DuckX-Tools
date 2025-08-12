import bpy
import bmesh
from bpy.types import (Operator)
from bpy.props import (EnumProperty, PointerProperty, StringProperty, FloatVectorProperty, FloatProperty, IntProperty, BoolProperty)

from ..icon_reg import *
from . import func_core
from ..ui import add_panel, add_expand_panel


class Duckx_OT_DistanceCalculator(Operator):
    bl_idname = "duckx_tools.distance_calculator"
    bl_label = "Distance Calculator"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Calculate distance from 2 objects"

    @classmethod
    def poll(cls, context):
        return context is not None and len(context.selected_objects) == 2

    def execute(self, context):
        try:
            d = func_core.distance_calculator()
            unit = context.scene.unit_settings.length_unit or 'METERS'
            msg = f"Distance: {d}"
            func_core.message_box(msg, self.bl_label, "CON_DISTLIMIT")
            self.report({'INFO'}, f"Distance: {d:.6f} {func_core.unit_short(unit)}")
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}



def draw_flip_tools(self, context, layout, props):
    row = layout.row(align=True)
    row.scale_y = 1.5
    row.scale_x = 5
    row.operator("duckx_tools.flip_tools", text="", icon_value=iconLib("giz_X")).axis = 'X'
    row.operator("duckx_tools.flip_tools", text="", icon_value=iconLib("giz_Y")).axis = 'Y'
    row.operator("duckx_tools.flip_tools", text="", icon_value=iconLib("giz_Z")).axis = 'Z'
    return layout

class Duckx_OT_EdgeLength(Operator):
    bl_idname = "duckx_tools.edge_length"
    bl_label = "Utilities Tools"
    bl_description = "Utilities Tools"


    def execute(self, context):
        msg, err = func_core.edge_length(context)
        if err:
            self.report({'WARNING'}, err)
            return {'CANCELLED'}
        try:
            func_core.message_box(msg, "Edge Length", "CON_DISTLIMIT")
            self.report({'INFO'}, msg)
        except Exception:
            self.report({'INFO'}, msg)
        return {'FINISHED'}




classes = [Duckx_OT_DistanceCalculator, Duckx_OT_EdgeLength]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
           
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)