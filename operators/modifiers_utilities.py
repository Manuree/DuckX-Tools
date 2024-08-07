import bpy
from bpy.types import (Operator)
from bpy.props import (EnumProperty, PointerProperty, StringProperty, FloatVectorProperty, FloatProperty, IntProperty, BoolProperty)

class Duckx_OT_DelModifiers(Operator):
    bl_idname = "duckx_tools.del_modifiers_operator"
    bl_label = "Delete Modifiers"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_icon = "MOD_MIRROR"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Tools for Delete Modifiers"
    
    action : StringProperty(name="Flip Axis")
    
    @classmethod
    def poll(cls, context):
        return context.selected_objects and context.mode == 'OBJECT'
    
    def execute(self, context):
        action = self.action
        scene = context.scene
        duckx_tools = scene.duckx_tools

        if action == "by_name":
            selected_objects = bpy.context.selected_objects
            for obj in selected_objects:
                modifier_index = None
                for i, modifier in enumerate(obj.modifiers):
                    if modifier.name == duckx_tools.mod_name and obj.type == "MESH":
                        modifier_index = i
                        break  # Exit loop after finding the modifier

                if modifier_index is not None:
                    # Use modifier index to ensure correct removal 
                    obj.modifiers.remove(obj.modifiers[modifier_index])
                else:
                    print(f"Warning: Modifier '{duckx_tools.mod_name}' not found on object '{obj.name}'.")
        
        return {'FINISHED'}
    
def register():
    bpy.utils.register_class(Duckx_OT_DelModifiers)
        
    
def unregister():
    bpy.utils.unregister_class(Duckx_OT_DelModifiers)
        