import bpy
import bmesh
import math

from . import func_core

from bpy.types import (Operator )
from bpy.props import (EnumProperty, PointerProperty, StringProperty, FloatVectorProperty, FloatProperty, IntProperty, BoolProperty)

class Duckx_OT_AlignToActive(Operator):
    bl_idname = "duckx_tools.align_to_active_operator"
    bl_label = "Align ToA ctive"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_icon = "EMPTY_ARROWS"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "SHIFT CLICK for ignore axis"

    axis : EnumProperty(
        name = "Axis",
        items = [('x', "X", ""),('y', "Y", ""),('z', "Z", "")]
        )
    flip : BoolProperty(name="Flip Axis", default=False)
    ignore = False


    def invoke(self, context, event):
        self.flip = False
        if event.shift:
            self.ignore = True
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
            bpy.ops.transform.resize(value=(0, 1, 1))
            a = (1, 0, 1)
            b = (1, 1, 0)
        elif axis == "y":
            bpy.ops.transform.resize(value=(1, 0, 1))
            a = (0, 1, 1)
            b = (1, 1, 0)
        elif axis == "z":
            bpy.ops.transform.resize(value=(1, 1, 0))
            a = (0, 1, 1)
            b = (1, 0, 1)
        
        if self.flip:
            a, b = b, a
        
        if self.ignore:
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


    
def register():
    bpy.utils.register_class(Duckx_OT_AlignToActive)
        
    
def unregister():
    bpy.utils.unregister_class(Duckx_OT_AlignToActive)
        
