import bpy
import bmesh
import math

from bpy.types import (Operator )
from bpy.props import (EnumProperty, PointerProperty, StringProperty, FloatVectorProperty, FloatProperty, IntProperty, BoolProperty)

from ..icon_reg import *
from . import func_core
from ..ui import add_panel, add_expand_panel

class Duckx_OT_AlignToActive(Operator):
    bl_idname = "duckx_tools.align_to_active"
    bl_label = "Align ToA ctive"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_icon = "EMPTY_ARROWS"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "SHIFT CLICK for ignore axis \nALT CLICK for collapse 2 vertex wihout this axis"

    axis : EnumProperty(
        name = "Axis",
        items = [('x', "X", ""),('y', "Y", ""),('z', "Z", "")]
        )
    flip : BoolProperty(name="Flip Axis", default=False)
    ignore = False
    two_vetex = False

    @classmethod
    def poll(cls, context):
        return (context.object is not None and 
                context.object.type == 'MESH' and 
                context.mode == 'EDIT_MESH')

    def invoke(self, context, event):
        self.flip = False
        if event.shift:
            self.ignore = True
        if event.alt:
            self.two_vetex = True
        return self.execute(context)

    def execute(self, context):
        pivot = bpy.context.scene.tool_settings.transform_pivot_point
        orient = bpy.context.scene.transform_orientation_slots[0].type

        obj = bpy.context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        vertex_list = []
        for element in bm.select_history:
            if isinstance(element, bmesh.types.BMVert):
                vertex_list.append(element)
        bpy.context.scene.tool_settings.transform_pivot_point = 'ACTIVE_ELEMENT'

        axis = self.axis
        if axis == "x":
            if self.ignore:
                bpy.ops.transform.resize(value=(1, 0, 0))
            else:
                bpy.ops.transform.resize(value=(0, 1, 1))
            a = (1, 0, 1)
            b = (1, 1, 0)
        elif axis == "y":
            if self.ignore:
                bpy.ops.transform.resize(value=(0, 1, 0))
            else:
                bpy.ops.transform.resize(value=(1, 0, 1))
            a = (0, 1, 1)
            b = (1, 1, 0)
        elif axis == "z":
            if self.ignore:
                bpy.ops.transform.resize(value=(0, 0, 1))
            else:
                bpy.ops.transform.resize(value=(1, 1, 0))
            a = (0, 1, 1)
            b = (1, 0, 1)
        
        if self.flip:
            a, b = b, a
        
        if self.two_vetex:
            try:
                bpy.ops.transform.resize(value=a)
                bpy.ops.mesh.select_all(action='DESELECT')
                vertex_list[1].select = True
                bm.select_history.clear()  # เคลียร์ประวัติการเลือกก่อนหน้า
                bm.select_history.add(vertex_list[0])
                vertex_list[0].select = True
                bpy.ops.transform.resize(value=b)
                bpy.ops.mesh.merge(type='CENTER')
            except:
                pass
            

        print(vertex_list)


        bmesh.update_edit_mesh(me)
        
        bpy.context.scene.tool_settings.transform_pivot_point = pivot
        bpy.context.scene.transform_orientation_slots[0].type = orient
        return {'FINISHED'}

def draw_align_tools(self, context, layout, props):
    col = layout.column(align=True)
    col.label(text="Align To Active")
    row = col.row(align=True)
    row.alignment = "CENTER"
    row.scale_y = 1.5
    row.scale_x = 5
    bt = row.operator("duckx_tools.align_to_active", text="", icon_value=iconLib("giz_X"))
    bt.axis = "x"
    bt = row.operator("duckx_tools.align_to_active", text="", icon_value=iconLib("giz_Y"))
    bt.axis = "y"
    bt = row.operator("duckx_tools.align_to_active", text="", icon_value=iconLib("giz_Z"))
    bt.axis = "z"
    return layout



add_expand_panel("Align", draw_align_tools, "MESH")
    
def register():
    bpy.utils.register_class(Duckx_OT_AlignToActive)
        
    
def unregister():
    bpy.utils.unregister_class(Duckx_OT_AlignToActive)
        
