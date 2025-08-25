import bpy
from bpy.types import Scene
from bpy.types import (PropertyGroup)
from bpy.props import (EnumProperty, PointerProperty, StringProperty, FloatVectorProperty, FloatProperty, IntProperty, BoolProperty)

import json
import string
import sys, pkgutil, importlib
import os   

from .icon_reg import *
from .ui import add_panel, add_expand_panel
from .operators import func_core

# ---------------------
# Leaf items
# ---------------------
class Duckx_ObjectItem(bpy.types.PropertyGroup):
    obj: PointerProperty(type=bpy.types.Object) # type: ignore

class Duckx_CollectionItem(bpy.types.PropertyGroup):
    col: PointerProperty(type=bpy.types.Collection) # type: ignore

# ---------------------
# Group (holds either objects or collections)
# ---------------------
class Duckx_Group(bpy.types.PropertyGroup):
    name: StringProperty(name="Group Name", default="Group")# type: ignore
    kind: EnumProperty(
        name="Kind",
        items=[
            ("OBJECTS", "Objects", "Hold objects"),
            ("COLLECTIONS", "Collections", "Hold collections"),
        ],
        default="OBJECTS",
    ) # type: ignore
    objects: bpy.props.CollectionProperty(type=Duckx_ObjectItem)# type: ignore
    collections: bpy.props.CollectionProperty(type=Duckx_CollectionItem)# type: ignore

    # indices for UIList (เผื่อทำ UI)
    obj_index: bpy.props.IntProperty(default=-1)# type: ignore
    col_index: bpy.props.IntProperty(default=-1)# type: ignore

# ---------------------
# Tab (holds groups)
# ---------------------
class Duckx_Tab(PropertyGroup):
    name: bpy.props.StringProperty(name="Tab Name", default="Tab")# type: ignore
    groups: bpy.props.CollectionProperty(type=Duckx_Group)# type: ignore
    group_index: bpy.props.IntProperty(default=-1)# type: ignore

_ADDON_READY = False
def update_overlays_settings(self, context):
    # กันช่วงยังไม่พร้อม / ยังไม่ผูก pointer
    if not _ADDON_READY or context is None or not hasattr(context.scene, "duckx_tools"):
        return

    try:
        settings = func_core.read_json("setting.json") or {}
    except Exception:
        settings = {}

    settings["overlay_correct_face_att"] = bool(self.overlay_correct_face_att)
    settings["overlay_uv_rotation"]      = bool(self.overlay_uv_rotation)
    settings["overlay_boundary_tools"]   = bool(self.overlay_boundary_tools)

    try:
        func_core.write_json("setting.json", settings)
    except Exception as e:
        print(f"[Duckx] write settings failed: {e}")

class Duckx_Properties(PropertyGroup):
    tabs_menu : EnumProperty(
        name = "Tabs",
        items = [('MESH', "Mesh", "Tools for mesh", bl_icons("FACE_MAPS"), 1),
                 ('UV', "UV", "Tools for UV", bl_icons("UV"), 2),
                 ('INS', "Instance", "Tools for Instance", bl_icons("NODETREE"), 3),
                 ('UTIL', "Utility", "Utility Tools", bl_icons("CONSOLE"), 4),
                 ('VIEW', "View", "Tools for view and display", bl_icons("WORKSPACE"), 5),
                 ('FILE_RENDER', "File and Render", "Tools for File and Render", bl_icons("OUTPUT"), 6),
                 ('SETTING', "Setting", "Addon setting", bl_icons("PREFERENCES"), 7)
                 ]
    )# type: ignore

    # Draw Overlay
    overlay_correct_face_att : BoolProperty(name="Correct Face Attributes", default=True, update=update_overlays_settings)# type: ignore
    overlay_uv_rotation : BoolProperty(name="UV Rotation", default=True, update=update_overlays_settings)# type: ignore
    overlay_boundary_tools : BoolProperty(name="Boundary Tools", default=True, update=update_overlays_settings)# type: ignore

    # Object Info
    uvmaps : BoolProperty(name="UV Maps", default=True)# type: ignore
    custom_props : BoolProperty(name="Custom Properties", default=False)# type: ignore
    filter_props : StringProperty(name="Filter Properties")# type: ignore

    # Object tools
    obj_color : FloatVectorProperty(name="Color", subtype='COLOR', size=4, min=0, max=1, default=(0.0, 0.0, 0.0, 1.0),)# type: ignore
    name_to_mesh : BoolProperty(name="Mesh Data Name Tools Toggle", default=True)# type: ignore
    uvmap_set_type : EnumProperty(
        name = "Type",
        items = [('name', "Name", ""),
                 ('index', "Index", "")
                 ]
    )# type: ignore

    # UV Tools
    uvmap_set_type : EnumProperty(
        name = "Type",
        items = [('name', "Name", ""),
                 ('index', "Index", "")
                 ]
    )# type: ignore
    uvmap_name : StringProperty(name="UV Map Name", default="UVMap")# type: ignore
    uvmap_index : IntProperty(name="UV Map Index", min=1, default=1)# type: ignore
    uv_angle : FloatProperty(name="UV Angle", step=1, default=0.0, precision=2)# type: ignore

    #Select from index
    select_type : EnumProperty(
        name = "Select Type",
        items = [('vertex', "Vertex", ""),
                 ('edge', "Edge", ""),
                 ('face', "Face", "")
                 ]
    )# type: ignore
    select_index_number : IntProperty(name="Index", default=0, min=0)# type: ignore


    tabs: bpy.props.CollectionProperty(type=Duckx_Tab) # type: ignore
    tab_index: bpy.props.IntProperty(default=-1) # type: ignore

    # Setting
    groups_panel : BoolProperty(name="Groups Panel", default=True)# type: ignore
    decals_panel : BoolProperty(name="Decale Panel", default=False)# type: ignore



# --- Auto-import _props ---
def _gather_props_from_here():
    props = {}
    # ใช้ package module ของโฟลเดอร์นี้ (operators) โดยตรง
    pkg = sys.modules[__package__]   # e.g. "your_addon.operators"
    # เดินทุกไฟล์/โฟลเดอร์ย่อยแบบ recursive: operators/, operators/func_core/, ...
    for finder, modname, ispkg in pkgutil.walk_packages(pkg.__path__, prefix=pkg.__name__ + "."):
        leaf = modname.rsplit(".", 1)[-1]
        if leaf in {"__init__", "properties"}:
            continue
        try:
            mod = importlib.import_module(modname)
        except Exception as e:
            print(f"[Duckx] skip import {modname}: {e}")
            continue
        pd = getattr(mod, "_props", None)
        if isinstance(pd, dict) and pd:
            print(f"[Duckx] Loaded props from {modname}: {list(pd.keys())}")
            props.update(pd)
    return props

def draw_setting(self, context, layout, props):
    row = layout.row(align=True)
    row.prop(props, "groups_panel")
    row.prop(props, "decals_panel")
    return layout

def draw_setting_overlay(self, context, layout, props):
    col = layout.column(align=True)
    col.prop(props, "overlay_correct_face_att")
    col.prop(props, "overlay_uv_rotation")
    col.prop(props, "overlay_boundary_tools")
    return layout



add_expand_panel("Panel Setting", draw_setting, "SETTING")
add_expand_panel("Overlay", draw_setting_overlay, "SETTING")




Duckx_Properties.__annotations__.update(_gather_props_from_here())
classes = [Duckx_ObjectItem, Duckx_CollectionItem, Duckx_Group, Duckx_Tab, Duckx_Properties]
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.duckx_tools = PointerProperty(type= Duckx_Properties)
    global _ADDON_READY
    _ADDON_READY = True 

def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

    global _ADDON_READY
    _ADDON_READY = False
    del Scene.duckx_tools
