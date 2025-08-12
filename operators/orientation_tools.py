import bpy
import bmesh
from bpy.types import (Operator)
from bpy.props import (EnumProperty, PointerProperty, StringProperty, FloatVectorProperty, FloatProperty, IntProperty, BoolProperty)

from ..icon_reg import *
from ..ui import add_panel, add_expand_panel

class Duckx_OT_OrientFromSelect(Operator):
    bl_idname = "duckx_tools.orienfromselect"
    bl_label = "Orient From Selection"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_description = "Make Orientation from Selection"
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
    bl_idname = "duckx_tools.orienglobal"
    bl_label = "Global"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_icon = "ORIENTATION_GLOBAL"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Back to orientation Global and remove Face orientation"

    pivot : EnumProperty(
        name = "Pivot",
        items = [('current', "Current", ""),
                ('bounding', "Bounding", ""),
                ('cursor', "Cursor", ""),
                ('individual', "Individual", ""),
                ('median', "Median", ""),
                ('active', "Active", "")
                ]
    )

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text="Pivot:")
        col.prop(self, "pivot", expand=True)

    
    def execute(self, context):
        if self.pivot == "bounding":
            pivot_point = "BOUNDING_BOX_CENTER"
        elif self.pivot == "cursor":
            pivot_point = "CURSOR"
        elif self.pivot == "individual":
            pivot_point = "INDIVIDUAL_ORIGINS"
        elif self.pivot == "median":
            pivot_point = "MEDIAN_POINT"
        elif self.pivot == "active":
            pivot_point = "ACTIVE_ELEMENT"
        else:
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
    bl_idname = "duckx_tools.orien_and_pivot"
    bl_label = "Orient And Pivot"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_icon = "ORIENTATION_GLOBAL"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Orientation and Pivot to 3D Cursor"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH' and context.mode == 'EDIT_MESH'

    def execute(self, context):
        bpy.ops.view3d.snap_cursor_to_active()
        bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'
        bpy.context.scene.tool_settings.transform_pivot_point = 'ACTIVE_ELEMENT'
        bpy.context.scene.transform_orientation_slots[0].type = 'NORMAL'


        return {'FINISHED'}

def draw_panel(self, context, layout, properties):
    col = layout.column(align=True)
    row = col.row(align=True)
    row.operator("duckx_tools.orienglobal", text="Global", icon=bl_icons("ORIENTATION_GLOBAL"))
    row.operator("duckx_tools.orienfromselect", text="Select", icon=bl_icons("EMPTY_ARROWS"))
    row.operator("duckx_tools.orien_and_pivot", text="Pivot", icon=bl_icons("PIVOT_CURSOR"))
    return row

add_panel("Orient Tools", draw_panel)
    
def register():
    bpy.utils.register_class(Duckx_OT_OrientFromSelect)
    bpy.utils.register_class(Duckx_OT_OrientGlobal)
    bpy.utils.register_class(Duckx_OT_OrientAndPivot)
        
    
def unregister():
    bpy.utils.unregister_class(Duckx_OT_OrientFromSelect)
    bpy.utils.unregister_class(Duckx_OT_OrientGlobal)
    bpy.utils.unregister_class(Duckx_OT_OrientAndPivot)
