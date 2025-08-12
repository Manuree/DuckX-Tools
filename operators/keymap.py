import bpy
from bpy.types import Operator
from bpy.props import (
    EnumProperty, StringProperty, BoolProperty
)

from ..icon_reg import *
from . import func_core
from ..ui import add_panel

# -----------------------------------------------------------------------------
# Properties contributed to DuckxProperties via _props (auto-collected)
# -----------------------------------------------------------------------------
ALPHA_ITEMS = tuple((ch, ch, f"Key {ch}") for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
_props = {
    "key_char":   EnumProperty(name="Key", description="Choose keyboard key", items=ALPHA_ITEMS, default="D"),  # type: ignore
    "use_ctrl":   BoolProperty(name="Ctrl",  description="Use Ctrl modifier",  default=False),                  # type: ignore
    "use_alt":    BoolProperty(name="Alt",   description="Use Alt modifier",   default=False),                  # type: ignore
    "use_shift":  BoolProperty(name="Shift", description="Use Shift modifier", default=False),                  # type: ignore
    "m_view_3d":  BoolProperty(name="3D View",  description="Affect 3D View keymap", default=True),            # type: ignore
    "m_uv_editor":BoolProperty(name="UV Editor", description="Affect UV Editor keymap", default=True),          # type: ignore
    "m_assigned_box": BoolProperty(name="Show Assigned", description="Show list of shortcuts using this key", default=False),  # type: ignore
}

# Menu we always add/remove (per request)
MENU_NAME = "OBJECT_MT_duckx_tools"

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
ADDON_KMS = []  # keep references so we can remove safely if needed

def _binding_matches(kmi, P):
    return (
        kmi.type == P.key_char and
        kmi.ctrl == P.use_ctrl and
        kmi.alt == P.use_alt and
        kmi.shift == P.use_shift and
        kmi.value == 'PRESS'
    )



def _iter_all_keymaps():
    wm = bpy.context.window_manager
    kcs = []
    for attr in ("addon", "user", "active", "default", "blender"):
        kc = getattr(wm.keyconfigs, attr, None)
        if kc and kc not in kcs:
            kcs.append(kc)
    for kc in kcs:
        for km in kc.keymaps:
            yield kc, km


def keymap_in_use(P):
    """Return [(area (config), op_id, extra)] for current key/mods across all keymaps.
    This lists everything bound to the key; it's read-only and does not affect add/remove.
    """
    result, seen = [], set()
    for kc, km in _iter_all_keymaps():
        for kmi in km.keymap_items:
            if not _binding_matches(kmi, P):
                continue
            extra = getattr(kmi.properties, "name", "") if kmi.idname == "wm.call_menu" else ""
            key = (kc.name, km.name, kmi.idname, extra)
            if key in seen:
                continue
            seen.add(key)
            result.append((f"{km.name} ({kc.name})", kmi.idname, extra))
    return result


# -----------------------------------------------------------------------------
# Operators (manual Add/Remove only – nothing auto on register)
# -----------------------------------------------------------------------------
MENU_NAME = "OBJECT_MT_duckx_tools"

class DUCKX_OT_KeymapAdd(bpy.types.Operator):
    bl_idname = "duckx_tools.keymap_add"
    bl_label = "Add Keymap"

    def _has_menu_binding(self, km, menu_name, key, ctrl, alt, shift):
        # เช็คว่ามี wm.call_menu ที่ name เดียวกัน + ปุ่ม/ม็อดิไฟเออร์เหมือนกันอยู่แล้วหรือยัง
        for kmi in km.keymap_items:
            if kmi.idname != "wm.call_menu":
                continue
            # บางครั้ง kmi.properties อาจไม่มี name (กัน error ไว้)
            if getattr(kmi.properties, "name", None) != menu_name:
                continue
            if (kmi.type == key and kmi.value == "PRESS" and
                kmi.ctrl == ctrl and kmi.alt == alt and kmi.shift == shift):
                return True
        
        
        return False

    def execute(self, context):
        prop = context.scene.duckx_tools

        if prop.m_view_3d:
            wm = bpy.context.window_manager
            kc = wm.keyconfigs.addon
            km = kc.keymaps.new(name="3D View", space_type="VIEW_3D", region_type="WINDOW")

            if not self._has_menu_binding(
                km, MENU_NAME, "D", prop.use_ctrl, prop.use_alt, prop.use_shift
            ):
                kmi = km.keymap_items.new(
                    "wm.call_menu", "D", "PRESS",
                    ctrl=prop.use_ctrl, alt=prop.use_alt, shift=prop.use_shift
                )
                kmi.properties.name = MENU_NAME

        if prop.m_uv_editor:
            wm = bpy.context.window_manager
            kc = wm.keyconfigs.addon
            km = kc.keymaps.new(name="UV Editor", space_type="EMPTY", region_type="WINDOW")

            if not self._has_menu_binding(
                km, MENU_NAME, "D", prop.use_ctrl, prop.use_alt, prop.use_shift
            ):
                kmi = km.keymap_items.new(
                    "wm.call_menu", "D", "PRESS",
                    ctrl=prop.use_ctrl, alt=prop.use_alt, shift=prop.use_shift
                )
                kmi.properties.name = MENU_NAME

        settings = func_core.read_json("setting.json")
        settings["Keymap Assign"] = True
        func_core.write_json("setting.json", settings)

        bpy.ops.wm.save_userpref()
        self.report({'INFO'}, f"Keymap ensured for {MENU_NAME} (no duplicates).")
        return {'FINISHED'}


class DUCKX_OT_KeymapRemove(bpy.types.Operator):
    bl_idname = "duckx_tools.keymap_remove"
    bl_label = "Remove Keymap"

    def execute(self, context):
        wm = bpy.context.window_manager
        kc = wm.keyconfigs.addon
        if kc is None:
            self.report({'ERROR'}, "No addon keyconfig available.")
            return {'CANCELLED'}

        removed_count = 0
        # ตรวจทุก keymap ใน addon keyconfig
        for km in kc.keymaps:
            for kmi in list(km.keymap_items):
                if kmi.idname == "wm.call_menu" and getattr(kmi.properties, "name", None) == MENU_NAME:
                    km.keymap_items.remove(kmi)
                    removed_count += 1

        settings = func_core.read_json("setting.json")
        settings["Keymap Assign"] = False
        func_core.write_json("setting.json", settings)

        bpy.ops.wm.save_userpref()
        self.report({'INFO'}, f"Removed {removed_count} keymap item(s) for {MENU_NAME}")
        return {'FINISHED'}


# -----------------------------------------------------------------------------
# UI
# -----------------------------------------------------------------------------

def draw_keymap(self, context, layout, properties):
    box = layout.box()
    row = box.row()
    row.label(text="Keymap")

    row = box.row(align=True)
    row.scale_x = 1.5; row.scale_y = 1.5
    row.prop(properties, "key_char", text="")
    row.prop(properties, "use_shift", text="", icon_value=iconLib("keymap_shift"))
    row.prop(properties, "use_ctrl",  text="", icon_value=iconLib("keymap_ctrl"))
    row.prop(properties, "use_alt",   text="", icon_value=iconLib("keymap_alt"))

    row = box.row(align=True); row.alignment = "CENTER"; row.scale_x = 5
    row.prop(properties, "m_view_3d",   text="", icon=bl_icons("VIEW3D"))
    row.prop(properties, "m_uv_editor", text="", icon=bl_icons("UV"))

    row = box.row(align=True); row.scale_y = 1.5
    row.operator("duckx_tools.keymap_add",    text="Add",    icon="ADD")
    row.operator("duckx_tools.keymap_remove", text="Remove", icon="REMOVE")

    used = keymap_in_use(properties)
    box2 = box.box()
    row = box2.row()
    row.prop(properties, "m_assigned_box", text="")
    row.label(text="Assigned Shortcuts")
    if properties.m_assigned_box:
        if not used:
            box2.label(text="(none)")
        else:
            for area_name, op_id, extra in used:
                box2.label(text=f"{area_name}: {extra or op_id}")


add_panel("Keymap", draw_keymap)


def register():
    bpy.utils.register_class(DUCKX_OT_KeymapAdd)
    bpy.utils.register_class(DUCKX_OT_KeymapRemove)


def unregister():
    bpy.utils.unregister_class(DUCKX_OT_KeymapAdd)
    bpy.utils.unregister_class(DUCKX_OT_KeymapRemove)
