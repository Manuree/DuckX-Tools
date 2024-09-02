import bpy

from . import func_core

from bpy.types import (Operator )
from bpy.props import (EnumProperty, PointerProperty, StringProperty, FloatVectorProperty, FloatProperty, IntProperty, BoolProperty)

class Duckx_OT_ObjectColors(Operator):
    bl_idname = "duckx_tools.object_colors"
    bl_label = "Object Colors"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_icon = "MOD_ARRAY"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Object Colors in viewport"

    action : StringProperty(name="action")

    @classmethod
    def poll(cls, context):
        return context.selected_objects
    
    def execute(self, context):
        scene = context.scene
        duckx_tools = scene.duckx_tools
        if self.action == "set":
            selected_objects = bpy.context.selected_objects
            for obj in selected_objects:
                obj.color = duckx_tools.obj_color
        elif self.action == "select":
            active_object = bpy.context.active_object
            for obj in bpy.context.scene.objects:
                if func_core.compare_colors(obj.color, active_object.color):
                    print(obj.name)
                    obj.select_set(True)
                    bpy.context.view_layer.objects.active = obj
                else:
                    obj.select_set(False)
        elif self.action == "pick":
            duckx_tools.obj_color = active_object = bpy.context.active_object.color
        return {'FINISHED'}

class Duckx_OT_ObjectWire(Operator):
    bl_idname = "duckx_tools.object_wire"
    bl_label = "Object Wireframe"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_icon = "MOD_ARRAY"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Wireframe"

    #action : StringProperty(name="action")
    action : EnumProperty(
        name = "Property",
        items = [("toggle", "Toggle", ""),
                 ("select", "Select all", ""),
                 ("showall", "Show all", "")
                 ]
    )

    @classmethod
    def poll(cls, context):
        return context.selected_objects
    
    def execute(self, context):
        if self.action == "toggle":
            selected_objects = bpy.context.selected_objects
            for obj in selected_objects:
                if obj.display_type != "WIRE" and obj.type == "MESH":
                    obj.display_type = 'WIRE'
                else:
                    obj.display_type = 'TEXTURED'
        elif self.action == "select":
            for obj in bpy.context.scene.objects:
                if obj.display_type == "WIRE" and obj.type == "MESH":
                    print(obj.name)
                    obj.select_set(True)
                    bpy.context.view_layer.objects.active = obj
                else:
                    obj.select_set(False)
        elif self.action == "showall":
            for obj in bpy.context.scene.objects:
                if obj.display_type == "WIRE" and obj.type == "MESH":
                    print(obj.name)
                    obj.select_set(True)
                    obj.display_type = 'TEXTURED'
                    bpy.context.view_layer.objects.active = obj
                else:
                    obj.select_set(False)
        return {'FINISHED'}
    
class Duckx_OT_DelCustomProp(Operator):
    bl_idname = "duckx_tools.del_custom_prop_operator"
    bl_label = "Delete All Custom Properties"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_icon = "CON_TRANSFORM"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Delete all custom properties"

    @classmethod
    def poll(cls, context):
        return context.selected_objects
    
    def execute(self, context):
        obj = bpy.context.object

        # Check if the object is valid and has custom properties
        if obj and obj.type == 'MESH' and obj.keys():
            # Create a copy of the custom property names
            custom_props = list(obj.keys())
            
            # Delete all custom properties
            for prop_name in custom_props:
                del obj[prop_name]
                print("Deleted custom property:", prop_name)
        else:
            print("No valid object selected or object has no custom properties.")

        return {'FINISHED'}


    
def register():
    bpy.utils.register_class(Duckx_OT_ObjectColors)
    bpy.utils.register_class(Duckx_OT_ObjectWire)
    bpy.utils.register_class(Duckx_OT_DelCustomProp)
           
def unregister():
    bpy.utils.unregister_class(Duckx_OT_ObjectColors)
    bpy.utils.unregister_class(Duckx_OT_ObjectWire)
    bpy.utils.unregister_class(Duckx_OT_DelCustomProp)
        
