import bpy
import bmesh
from bpy.types import (Operator)
from bpy.props import (EnumProperty, PointerProperty, StringProperty, FloatVectorProperty, FloatProperty, IntProperty, BoolProperty)

from ..icon_reg import *
from . import func_core
from ..ui import add_panel, add_expand_panel

class Duckx_OT_FlipTools(Operator):
    bl_idname = "duckx_tools.flip_tools"
    bl_label = "Flip Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Flip Tools - Flip objects around Global Origin or 3D Cursor \n[SHIFT CLICK] for 3D Cursor"

    action : EnumProperty(name="Action",
                          items=[
            ('GLOBAL', "Global", "Flip around Global Origin"),
            ('CURSOR', "Cursor", "Flip around 3D Cursor")
        ],
        default='GLOBAL'
    )
    
    axis : EnumProperty(name="Axis",
                          items=[
            ('X', "X", "X Axis"),
            ('Y', "Y", "Y Axis"),
            ('Z', "Z", "Z Axis")
        ],
        default='X'
    )

    @classmethod
    def poll(cls, context):
        return (context.object is not None and 
                context.object.type == 'MESH')
    
    def invoke(self, context, event):
        if event.shift:
            self.action = "CURSOR"
        else:
            self.action = "GLOBAL"
        return self.execute(context)

    def execute(self, context):
        # Set transform pivot based on action
        objs = context.selected_objects
        original_pivot = context.scene.tool_settings.transform_pivot_point
        
        if self.action == 'GLOBAL':
            # Set 3D Cursor
            original_cursor = func_core.store_cursor_position()
            bpy.ops.view3d.snap_cursor_to_center()
            # Set pivot to median point (global origin)
            bpy.ops.duckx_tools.orienglobal()
            bpy.ops.view3d.snap_cursor_to_center()
            context.scene.tool_settings.transform_pivot_point = 'CURSOR'
            # Flip around global origin
            if self.axis == 'X':
                bpy.ops.transform.resize(value=(-1, 1, 1))
            elif self.axis == 'Y':
                bpy.ops.transform.resize(value=(1, -1, 1))
            elif self.axis == 'Z':
                bpy.ops.transform.resize(value=(1, 1, -1))
            
            func_core.restore_cursor_position(original_cursor)
            

        elif self.action == 'CURSOR':
            # Set pivot to 3D cursor
            context.scene.tool_settings.transform_pivot_point = 'CURSOR'
            # Flip around 3D cursor
            if self.axis == 'X':
                bpy.ops.transform.resize(value=(-1, 1, 1))
            elif self.axis == 'Y':
                bpy.ops.transform.resize(value=(1, -1, 1))
            elif self.axis == 'Z':
                bpy.ops.transform.resize(value=(1, 1, -1))

        # If in Edit mode, recalculate normals after flipping
        if context.mode == 'EDIT_MESH':
            bpy.ops.mesh.normals_make_consistent(inside=False)
        
        # Restore original pivot point
        context.scene.tool_settings.transform_pivot_point = original_pivot
        if context.mode == 'OBJECT':
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.flip_normals()
            bpy.ops.object.mode_set(mode='OBJECT')
        
        
        self.report({'INFO'}, f"Flipped around {self.action.title()} on {self.axis} axis")
        
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.scale_y = 1.5
        row.prop(self, "action", expand=True)
        row = layout.row(align=True)
        row.prop(self, "axis", expand=True)
    

def draw_flip_tools(self, context, layout, props):
    row = layout.row(align=True)
    row.scale_y = 1.5
    row.scale_x = 5
    row.operator("duckx_tools.flip_tools", text="", icon_value=iconLib("giz_X")).axis = 'X'
    row.operator("duckx_tools.flip_tools", text="", icon_value=iconLib("giz_Y")).axis = 'Y'
    row.operator("duckx_tools.flip_tools", text="", icon_value=iconLib("giz_Z")).axis = 'Z'
    return layout



add_expand_panel("Flip", draw_flip_tools)



classes = [Duckx_OT_FlipTools]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
           
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)