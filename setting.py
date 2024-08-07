import bpy
from bpy.types import (Operator)
from bpy.props import (EnumProperty, PointerProperty, StringProperty, FloatVectorProperty, FloatProperty, IntProperty, BoolProperty)

class Duckx_OT_DuckxKeymap(Operator):
    bl_idname = "duckx_tools.duckx_keymap_operator"
    bl_label = "DuckX Setting"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_description = "Toggle Setting"
    bl_options = {"REGISTER", "UNDO"}
    
    action : StringProperty(name="Action")
    def execute(self, context):
        action = self.action
        
        if action == "add":
            # Create the keymap entry in Object Mode
            wm = bpy.context.window_manager
            kc = wm.keyconfigs.addon
            if kc:
                km = kc.keymaps.new(name="Object Mode", space_type="EMPTY")
                kmi = km.keymap_items.new("wm.call_menu", "D", "PRESS", ctrl=False)
                kmi.properties.name = "OBJECT_MT_duckx_tools"

            # Create the keymap entry in Edit Mode
            if kc:
                km = kc.keymaps.new(name="Mesh", space_type="EMPTY", region_type="WINDOW")
                kmi = km.keymap_items.new("wm.call_menu", "D", "PRESS", ctrl=False)
                kmi.properties.name = "OBJECT_MT_duckx_tools"
                
            # Create the keymap entry in UV Mode
            if kc:
                km = kc.keymaps.new(name="UV Editor", space_type="EMPTY", region_type="WINDOW")
                kmi = km.keymap_items.new("wm.call_menu", "D", "PRESS", ctrl=False)
                kmi.properties.name = "OBJECT_MT_duckx_tools"
        elif action == "remove":
            # Remove the keymap entries
            wm = bpy.context.window_manager
            kc = wm.keyconfigs.addon
            if kc:
                # Remove the keymap entry in Object Mode
                km = kc.keymaps["Object Mode"]
                for kmi in km.keymap_items:
                    if kmi.properties.name == "OBJECT_MT_duckx_tools":
                        km.keymap_items.remove(kmi)
                        break
                
                # Remove the keymap entry in Edit Mode
                km = kc.keymaps["Mesh"]
                for kmi in km.keymap_items:
                    if kmi.properties.name == "OBJECT_MT_duckx_tools":
                        km.keymap_items.remove(kmi)
                        break
                
                # Remove the keymap entry in Edit Mode
                km = kc.keymaps["UV Editor"]
                for kmi in km.keymap_items:
                    if kmi.properties.name == "OBJECT_MT_duckx_tools":
                        km.keymap_items.remove(kmi)
                        break

        return {'FINISHED'}

    
def register():
    bpy.utils.register_class(Duckx_OT_DuckxKeymap)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name="Object Mode", space_type="EMPTY")
        kmi = km.keymap_items.new("wm.call_menu", "D", "PRESS", ctrl=False)
        kmi.properties.name = "OBJECT_MT_duckx_tools"

    # Create the keymap entry in Edit Mode
    if kc:
        km = kc.keymaps.new(name="Mesh", space_type="EMPTY", region_type="WINDOW")
        kmi = km.keymap_items.new("wm.call_menu", "D", "PRESS", ctrl=False)
        kmi.properties.name = "OBJECT_MT_duckx_tools"
        
    # Create the keymap entry in UV Mode
    if kc:
        km = kc.keymaps.new(name="UV Editor", space_type="EMPTY", region_type="WINDOW")
        kmi = km.keymap_items.new("wm.call_menu", "D", "PRESS", ctrl=False)
        kmi.properties.name = "OBJECT_MT_duckx_tools"
        
    
def unregister():
    bpy.utils.unregister_class(Duckx_OT_DuckxKeymap)
        
