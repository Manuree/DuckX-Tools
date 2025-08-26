import bpy
from bpy.types import AddonPreferences
from bpy.props import (
    BoolProperty, IntProperty, FloatVectorProperty, FloatProperty
)

# ปรับ import ให้ตรงแพ็กเกจคุณ
from .operators.func_core import draw_handler as dh


ADDON_ID = __package__

def get_prefs():
    """ใช้เรียก prefs จากไฟล์อื่น ๆ ได้อย่างปลอดภัย"""
    addon = bpy.context.preferences.addons.get(ADDON_ID)
    return addon.preferences if addon else None

def _prefs():
    """คืนค่า preferences ของแอดออนนี้อย่างปลอดภัย"""
    addon = bpy.context.preferences.addons.get(__package__)
    return getattr(addon, "preferences", None) if addon else None


def _apply_frame_from_prefs():
    """ทำให้ draw handler สอดคล้องกับค่าใน Preferences"""
    pr = _prefs()
    if not pr:
        return
    if pr.overlay_frame_enable:
        dh.draw_handler_start(
            color=tuple(pr.overlay_frame_color),
            thickness=pr.overlay_frame_thickness,
            margin=pr.overlay_frame_margin,
        )
    else:
        dh.draw_handler_stop()


class DuckXPrefs(AddonPreferences):
    bl_idname = ADDON_ID  # ให้ตรงชื่อแพ็กเกจของแอดออน

    # Custom color
    overlay_custom_color: BoolProperty(
        name="Custom Color",default=False,
        description="Enable custom color for all overlay",)

    # ----- Overlay flags (ตัวเดียวกับที่คุณเคยเก็บใน JSON/Scene) -----
    overlay_correct_face_att: BoolProperty(
        name="Correct Face Attributes",
        default=True,
        description="Show overlay for correcting face attributes",
    )
    overlay_uv_rotation: BoolProperty(
        name="UV Rotation",
        default=True,
        description="Show overlay for UV rotation helper",
    )
    overlay_boundary_tools: BoolProperty(
        name="Boundary Tools",
        default=True,
        description="Show overlay for boundary tools",
    )

    # ----- Frame (กรอบสีเขียว) -----
    overlay_frame_enable: BoolProperty(
        name="Show Green Frame",
        default=False,
        description="Draw a frame overlay in the 3D View",
        update=lambda self, ctx: _apply_frame_from_prefs()
    )

    overlay_frame_color: FloatVectorProperty(
        name="Frame Color",
        subtype="COLOR",
        size=4,
        min=0.0, max=1.0,
        default=(0.921577, 0.313989, 0.109462, 1),
        update=lambda self, ctx: _apply_frame_from_prefs()
    )
    overlay_frame_thickness: IntProperty(
        name="Thickness (px)",
        min=1, max=32,
        default=2,
        update=lambda self, ctx: _apply_frame_from_prefs()
    )
    overlay_frame_margin: IntProperty(
        name="Margin (px)",
        min=0, max=512,
        default=3,
        update=lambda self, ctx: _apply_frame_from_prefs()
    )

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        col.label(text="Overlays", icon="OVERLAY")
        col.prop(self, "overlay_correct_face_att")
        col.prop(self, "overlay_uv_rotation")
        col.prop(self, "overlay_boundary_tools")

        col.separator()
        box = col.box()
        row = box.row(align=True)
        row.prop(self, "overlay_frame_enable", toggle=True)
        row = box.row(align=True)
        row.prop(self, "overlay_frame_color", text="")
        row.separator()
        row.prop(self, "overlay_custom_color")
        box.prop(self, "overlay_frame_thickness")
        box.prop(self, "overlay_frame_margin")


# --- register hooks (ตัวอย่าง; รวมกับของเดิมคุณ) ---
classes = (DuckXPrefs,)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    # ถ้าผู้ใช้เปิดแอดออนตอนที่ Blender เปิดไฟล์อยู่แล้ว
    # ทำให้ draw handler ตรงกับค่าปัจจุบันของ prefs ทันที
    _apply_frame_from_prefs()


def unregister():
    # ปิดกรอบก่อนถอดคลาส (กัน handler ค้าง)
    pr = _prefs()
    if pr:
        dh.draw_handler_stop()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
