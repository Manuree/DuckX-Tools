import bpy

from . import func_core
from .. import icon_reg

from bpy.types import (Operator )
from bpy.props import (EnumProperty, PointerProperty, StringProperty, FloatVectorProperty, FloatProperty, IntProperty, BoolProperty)

class Duckx_OT_CollectionExport(Operator):
    bl_idname = "duckx_tools.collection_export_operator"
    bl_label = "Collection Export"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_icon = "EMPTY_ARROWS"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Export Collection"

    action : StringProperty(name="Action")
    data : StringProperty(name="Collection Data")

    def execute(self, context):
        scene = context.scene
        duckx_tools = scene.duckx_tools
        action = self.action
        selected_collection = bpy.context.view_layer.active_layer_collection.collection
        
        if action == "add_data":
            data = ["fbx", duckx_tools.export_path]
            selected_collection["Duckx Export Data"] = func_core.list_to_string(data)
            self.report({"INFO"} ,f"Added to Collection: {selected_collection['Duckx Export Data']}")
            
        elif action == "remove_data":
            export_data = func_core.get_collection_custom_property(selected_collection.name, "Duckx Export Data")
            if not export_data is None:
                del selected_collection["Duckx Export Data"]
                print("Custom property 'Duckx Export Data' removed.")
            else:
                print("Custom property 'Duckx Export Data' not found.")


        elif action == "export":
            active_collection = bpy.context.view_layer.active_layer_collection
            collection_name = active_collection.name
            
            export_data = func_core.string_to_list(func_core.get_collection_custom_property(active_collection.name, "Duckx Export Data"))
            if export_data is not None:
                print("Duckx Export Data:", export_data)
            else:
                self.report({"INFO"} ,f"None export data from Collection")
                return {'FINISHED'}
            
            # เส้นทางที่คุณต้องการจะบันทึกไฟล์ .fbx
            file_name = collection_name + ".fbx"
            export_path = export_data[1] + file_name

            def export_fbx():
                # คำสั่งสำหรับ Export .fbx
                bpy.ops.export_scene.fbx(
                filepath=export_path,
                check_existing=False,
                use_selection=False,
                object_types={'MESH', 'OTHER', 'EMPTY', 'ARMATURE'},
                use_custom_props=True,
                global_scale=1.0,
                add_leaf_bones=False, bake_anim=False)
            
            try:
                if export_data[0] == "fbx":
                    export_fbx()
                print(f"Exported to: {export_path}")
                self.report({"INFO"} ,f"Exported to: {export_path}")
            except:
                print(f"Export Error")
                self.report({"INFO"} ,f"Export Error")
                return {'FINISHED'}


        return {'FINISHED'}


def collection_export(self, context):
    selected_collection = bpy.context.view_layer.active_layer_collection.collection
    collection = bpy.data.collections.get(selected_collection.name)
    export_data = collection.get("Duckx Export Data")
    if not export_data is None:
        self.layout.operator("duckx_tools.collection_export_operator", text="Collection Export", icon_value=icon_reg.iconLib("duckx_icon")).action = "export"
    
def register():
    bpy.utils.register_class(Duckx_OT_CollectionExport)
    bpy.types.OUTLINER_MT_collection.prepend(collection_export)
        
    
def unregister():
    bpy.utils.unregister_class(Duckx_OT_CollectionExport)
    bpy.types.OUTLINER_MT_collection.remove(collection_export)
        
