import bpy
from bpy.types import (Operator )
from bpy.props import (EnumProperty, PointerProperty, StringProperty, FloatVectorProperty, FloatProperty, IntProperty, BoolProperty)

from collections import OrderedDict
from ..icon_reg import *
from . import func_core
from ..ui import add_panel, add_expand_panel

import json
import os
def _selected_collections_only(context):
    cols = func_core.collections_from_selected_objects(context)
    if not cols and context.view_layer and context.view_layer.active_layer_collection:
        cols = [context.view_layer.active_layer_collection.collection]
    return cols



class Duckx_OT_CollectionExport(bpy.types.Operator):
    bl_idname = "duckx_tools.collection_export"
    bl_label = "Collection Export"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_icon = "EMPTY_ARROWS"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Export Collection"

    # รับกุญแจกลุ่มจาก UI (JSON: {"file_path": "...", "file_type": "..."})
    group_key: bpy.props.StringProperty(name="Group Key")  # type: ignore

    def execute(self, context):
        print(f"xxxxxxxxxxxxxxxxxx- {self.group_key}")
        try:
            key = json.loads(getattr(self, "group_key", "") or "{}")
        except Exception:
            key = {}
        k_fp = key.get("file_path", "")
        k_ft = key.get("file_type", "")

        targets = []
        for coll in _selected_collections_only(context):
            ed = json.loads(coll.get("Duckx Export Data", "{}"))
            if not key or (ed.get("file_path", "") == k_fp and ed.get("file_type", "") == k_ft):
                targets.append((coll, ed))

        for coll, ed in targets:
            print(f"[DuckX][Export] {coll.name} | file_path='{ed.get('file_path','')}' | file_type='{ed.get('file_type','')}'")
            
            # เส้นทางที่คุณต้องการจะบันทึกไฟล์ .fbx
            file_type = ed.get('file_type','.fbx')
            file_name = coll.name + file_type
            export_path = ed.get('file_path','') + file_name

            def export_fbx():
                # คำสั่งสำหรับ Export .fbx
                bpy.ops.export_scene.fbx(
                filepath=export_path,
                check_existing=False,
                use_selection=False,
                object_types={'MESH', 'OTHER', 'EMPTY', 'ARMATURE'},
                use_custom_props=True,
                global_scale=1.0,
                add_leaf_bones=False, bake_anim=False,
                use_active_collection=True)
            try:
                if not os.path.exists(os.path.dirname(export_path)):
                    os.makedirs(os.path.dirname(export_path))
            except:
                self.report({"INFO"} ,f"Export Error")
                return {'CANCELLED'}
            try:
                if export_path != "":
                    if file_type == ".fbx":
                        export_fbx()
                    else:
                        self.report({"INFO"} ,f"Work Inprogress")
                        return {'FINISHED'}
                    print(f"Exported to: {export_path}")
                    self.report({"INFO"} ,f"Exported to: {export_path}")
            except:
                print(f"Export Error")
                self.report({"INFO"} ,f"Export Error")

        return {'FINISHED'}
    
class DUCKX_OT_PickExportPath(Operator):
    bl_idname = "duckx_tools.pick_export_path"
    bl_label  = "Pick Folder"

     # กลุ่มที่ต้องอัปเดต (JSON: {"file_path": "...", "file_type": "..."})
    group_key: StringProperty(name="Group Key")

    directory: StringProperty(subtype='DIR_PATH')

    def _default_dir(self, context):
        if self.directory:
            return self.directory
        if bpy.data.filepath:
            return os.path.dirname(bpy.path.abspath(bpy.data.filepath))
        return os.path.expanduser("~")

    def invoke(self, context, event):
        self.directory = self._default_dir(context)
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        d = bpy.path.abspath(self.directory)
        if d and not d.endswith(os.sep):
            d += os.sep
        self.directory = d

        try:
            key = json.loads(self.group_key) if getattr(self, "group_key", "") else {}
        except Exception:
            key = {}
        k_fp = key.get("file_path", "")
        k_ft = key.get("file_type", "")

        updated = 0
        for coll in _selected_collections_only(context):
            ed = json.loads(coll.get("Duckx Export Data", "{}"))
            if ed.get("file_path", "") == k_fp and ed.get("file_type", "") == k_ft:
                new_data = {
                    "file_path": self.directory,
                    "file_type": ed.get("file_type", k_ft or ".fbx"),
                    "file_setting": ed.get("file_setting", "")
                }
                coll["Duckx Export Data"] = json.dumps(new_data)
                updated += 1

        print(f"[DuckX] Updated {updated} selected collections to dir: {self.directory}")
        return {'FINISHED'}
    
class DUCKX_OT_PickFileType(Operator):
    bl_idname = "duckx_tools.pick_file_type"
    bl_label  = "Pick File Type"
    bl_description = "Choose export file type for all collections in the same group"

    # รับกุญแจกลุ่มจาก UI (JSON: {"file_path": "...", "file_type": "..."})
    group_key: StringProperty(name="Group Key")

    file_type: EnumProperty(
        name="File Type",
        items=[
            (".fbx", "FBX (.fbx)", "Export as FBX"),
            (".obj", "OBJ (.obj)", "Export as OBJ"),
        ],
        default=".fbx",
    )  # type: ignore

    # เก็บ settings เป็น JSON string (เผื่อใช้ภายหลัง)
    export_settings: StringProperty(
        name="Export Settings",
        default="{}"
    )  # type: ignore


    def invoke(self, context, event):
        # ถ้ามี group_key ให้ตั้งค่า file_type เริ่มต้นตามกลุ่มนั้น
        try:
            key = json.loads(self.group_key) if self.group_key else {}
        except Exception:
            key = {}
        cur_ft = key.get("file_type", "")
        if cur_ft in {".fbx", ".obj"}:
            self.file_type = cur_ft
        return context.window_manager.invoke_props_dialog(self, width=320)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "file_type", text="")

    def execute(self, context):
        try:
            key = json.loads(self.group_key) if getattr(self, "group_key", "") else {}
        except Exception:
            key = {}
        k_fp = key.get("file_path", "")
        k_ft = key.get("file_type", "")

        updated = 0
        for coll in _selected_collections_only(context):
            ed = json.loads(coll.get("Duckx Export Data", "{}"))
            if ed.get("file_path", "") == k_fp and ed.get("file_type", "") == k_ft:
                ed["file_type"] = self.file_type
                coll["Duckx Export Data"] = json.dumps(ed)
                updated += 1

        print(f"[DuckX] Set file_type='{self.file_type}' for {updated} selected collections in group.")
        try: func_core.refresh_panel()
        except: pass
        return {'FINISHED'}
    
class Duckx_OT_CollectionExportOutliner(bpy.types.Operator):
    bl_idname = "duckx_tools.collection_export_outliner"
    bl_label = "Collection Export"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_icon = "EMPTY_ARROWS"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Export Collection"

    def execute(self, context):
        cols = func_core.collections_from_selected_objects(context)
        print(cols)
        return {'FINISHED'}


def collection_export(self, context):
    selected_collection = bpy.context.view_layer.active_layer_collection.collection
    collection = bpy.data.collections.get(selected_collection.name)
    export_data = collection.get("Duckx Export Data")
    if not export_data is None:
        self.layout.operator("duckx_tools.collection_export", text="Collection Export", icon_value=iconLib("duckx_icon")).action = "export"


def draw_collection_export(self, context, layout, properties):
    box = layout.box()
    col = box.column(align=True)
    col.label(text="Collection Export")

    cols = func_core.collections_from_selected_objects(context)

    groups = OrderedDict()
    for c in cols:
        ed = json.loads(c.get("Duckx Export Data", "{}"))
        fp = ed.get("file_path", "") or ""
        ft = ed.get("file_type", "") or ""
        key = (fp, ft)
        groups.setdefault(key, {"file_path": fp, "file_type": ft, "cols": []})
        groups[key]["cols"].append(c)

    for (fp, ft), info in groups.items():
        sub_box = col.box()

        header = sub_box.row(align=True)
        for c in info["cols"]:
            header.label(text=c.name, icon=func_core.collection_color_icon(c))

        row = sub_box.row(align=True)
        if fp:
            row.label(text=fp)
        else:
            row.label(text="Please select folder")

        # ----- ส่ง group_key ลง operator -----
        group_key = json.dumps({"file_path": fp, "file_type": ft}, sort_keys=True)

        bt_ep = row.operator("duckx_tools.pick_export_path", text="", icon=bl_icons("FILEBROWSER"))
        bt_ep.group_key = group_key

        sub = row.split(factor=1, align=True)
        sub.scale_x = 0.5
        bt_ft = sub.operator("duckx_tools.pick_file_type", text=(ft if ft else ".fbx"))
        bt_ft.group_key = group_key
        bt_ex = row.operator("duckx_tools.collection_export", text="", icon=bl_icons("EXPORT"))
        bt_ex.group_key = group_key



def collection_export(self, context):
    selected_collection = bpy.context.view_layer.active_layer_collection.collection
    collection = bpy.data.collections.get(selected_collection.name)
    export_data = collection.get("Duckx Export Data")
    
    if not export_data is None:
        self.layout.operator("duckx_tools.collection_export", text="Collection Export", icon_value=iconLib("duckx_icon"))
        #bt_ex.group_key = group_key


add_panel("Collection Export", draw_collection_export)

def register():
    bpy.utils.register_class(Duckx_OT_CollectionExport)
    bpy.utils.register_class(DUCKX_OT_PickExportPath)
    bpy.utils.register_class(DUCKX_OT_PickFileType)
    bpy.types.OUTLINER_MT_collection.prepend(collection_export)
        
    
def unregister():
    bpy.utils.unregister_class(Duckx_OT_CollectionExport)
    bpy.utils.unregister_class(DUCKX_OT_PickExportPath)
    bpy.utils.unregister_class(DUCKX_OT_PickFileType)
    bpy.types.OUTLINER_MT_collection.remove(collection_export)
        
