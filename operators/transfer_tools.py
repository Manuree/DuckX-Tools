import bpy
from bpy.types import (Operator)
from bpy.props import (EnumProperty, PointerProperty, StringProperty, FloatVectorProperty, FloatProperty, IntProperty, BoolProperty)

from ..icon_reg import *
from . import func_core
from ..ui import add_panel, add_expand_panel



class Duckx_OT_TransferFromActive(Operator):
    bl_idname = "duckx_tools.transfer_from_active"
    bl_label = "Transfer From Active"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Transfer any from active object to selected ones"

    location_x: BoolProperty(name="Location", default=False)
    location_y: BoolProperty(name="Location", default=False)
    location_z: BoolProperty(name="Location", default=False)

    rotation_x: BoolProperty(name="Rotation", default=False)
    rotation_y: BoolProperty(name="Rotation", default=False)
    rotation_z: BoolProperty(name="Rotation", default=False)
    
    scale_x: BoolProperty(name="Scale", default=False)
    scale_y: BoolProperty(name="Scale", default=False)
    scale_z: BoolProperty(name="Scale", default=False)
    
    dimensions_x: BoolProperty(name="Dimensions", default=False)
    dimensions_y: BoolProperty(name="Dimensions", default=False)
    dimensions_z: BoolProperty(name="Dimensions", default=False)
    
    @classmethod
    def poll(cls, context):
        return (
            context.mode == 'OBJECT' and
            context.active_object is not None and
            len(context.selected_objects) > 1
        )

    def invoke(self, context, event):
        self.location_x = False
        self.location_y = False
        self.location_z = False
        self.rotation_x = False
        self.rotation_y = False
        self.rotation_z = False
        self.scale_x = False
        self.scale_y = False
        self.scale_z = False
        self.dimensions_x = False
        self.dimensions_y = False
        self.dimensions_z = False
       
        bpy.ops.wm.tool_set_by_id(name="builtin.move")

        # เรียก popup เพื่อให้ผู้ใช้เลือกแกน
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Copy Location:")
        row = layout.row(align=True)
        row.scale_y = 1.5
        row.prop(self, "location_x", icon_value=iconLib("giz_X"))
        row.prop(self, "location_y", icon_value=iconLib("giz_Y"))
        row.prop(self, "location_z", icon_value=iconLib("giz_Z"))
        row = layout.row(align=True)
        row.scale_y = 1.5
        row.prop(self, "rotation_x", icon_value=iconLib("giz_X"))
        row.prop(self, "rotation_y", icon_value=iconLib("giz_Y"))
        row.prop(self, "rotation_z", icon_value=iconLib("giz_Z"))
        row = layout.row(align=True)
        row.scale_y = 1.5
        if not (self.dimensions_x or self.dimensions_y or self.dimensions_z):
            row.prop(self, "scale_x", icon_value=iconLib("giz_X"))
            row.prop(self, "scale_y", icon_value=iconLib("giz_Y"))
            row.prop(self, "scale_z", icon_value=iconLib("giz_Z"))
        else:
            row.label(text="(Scale is disabled when Dimensions are selected)", icon=bl_icons("ERROR"))

        row = layout.row(align=True)
        row.scale_y = 1.5
        if not (self.scale_x or self.scale_y or self.scale_z):
            row.prop(self, "dimensions_x", icon_value=iconLib("giz_X"))
            row.prop(self, "dimensions_y", icon_value=iconLib("giz_Y"))
            row.prop(self, "dimensions_z", icon_value=iconLib("giz_Z"))
        else:
            row.label(text="(Dimensions is disabled when Scale are selected)", icon=bl_icons("ERROR"))

    def execute(self, context):
        active_obj = context.active_object
        selected_objs = context.selected_objects

        if not active_obj:
            self.report({'ERROR'}, "No active object found.")
            return {'CANCELLED'}

        for obj in selected_objs:
            if obj == active_obj:
                continue

            # Location
            loc = obj.location.copy()
            if self.location_x:
                loc.x = active_obj.location.x
            if self.location_y:
                loc.y = active_obj.location.y
            if self.location_z:
                loc.z = active_obj.location.z
            obj.location = loc

            # Rotation
            rot = obj.rotation_euler.copy()
            if self.rotation_x:
                rot.x = active_obj.rotation_euler.x
            if self.rotation_y:
                rot.y = active_obj.rotation_euler.y
            if self.rotation_z:
                rot.z = active_obj.rotation_euler.z
            obj.rotation_euler = rot

            if self.scale_x or self.scale_y or self.scale_z:
                # Scale
                sca = obj.scale.copy()
                if self.scale_x:
                    sca.x = active_obj.scale.x
                if self.scale_y:
                    sca.y = active_obj.scale.y
                if self.scale_z:
                    sca.z = active_obj.scale.z
                obj.scale = sca
            else:
                # Dimensions (must apply to object.dimensions directly)
                dims = obj.dimensions.copy()
                print(dims)
                if self.dimensions_x:
                    dims.x = active_obj.dimensions.x
                if self.dimensions_y:
                    dims.y = active_obj.dimensions.y
                if self.dimensions_z:
                    dims.z = active_obj.dimensions.z
                obj.dimensions = dims

        self.report({'INFO'}, "Transform copied from active object.")
        return {'FINISHED'}

def draw_transfer_from_active(self, context, layout, props):
    layout.scale_x = 5
    layout.operator("duckx_tools.transfer_from_active", text="", icon=bl_icons("EYEDROPPER"))
    return layout



add_panel("Tranfer_From_Active", draw_transfer_from_active)
    
def register():
    bpy.utils.register_class(Duckx_OT_TransferFromActive)
        
    
def unregister():
    bpy.utils.unregister_class(Duckx_OT_TransferFromActive)
        
