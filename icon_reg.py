import os
import bpy
import bpy.utils.previews as previews

preview_collections = {}  # อย่าให้ประกาศซ้ำหลายที่

AVAILABLE_ICONS = set(bpy.types.UILayout.bl_rna.functions["prop"]
                      .parameters["icon"].enum_items.keys())

def bl_icons(icon_name: str):
    return icon_name if icon_name in AVAILABLE_ICONS else "CONSOLE"

def iconLib(name="duckx_icon"):
    pcoll = preview_collections.get("main")
    if not pcoll or name not in pcoll:
        # ปลอดภัย: ถ้าไม่มี ให้คืนไอคอนเริ่มต้น
        return bpy.types.UILayout.icon(bpy.context.preferences)  # หรือ 0
    return pcoll[name].icon_id

def register():
    # ถ้ามี "main" อยู่แล้ว ให้ลบตัวเก่าก่อน (กันรั่วเวลา re-register)
    old = preview_collections.get("main")
    if old:
        try:
            previews.remove(old)
        except Exception:
            pass
        preview_collections.pop("main", None)

    pcoll = previews.new()
    try:
        icon_path = os.path.join(os.path.dirname(__file__), "icons")
        if os.path.isdir(icon_path):
            for entry in os.scandir(icon_path):
                if entry.is_file() and entry.name.lower().endswith(".png"):
                    name = os.path.splitext(entry.name)[0]
                    pcoll.load(name, os.path.join(icon_path, entry.name), 'IMAGE')
        else:
            # ไม่มีโฟลเดอร์ icons ก็ไม่เป็นไร แค่ไม่โหลดอะไร
            pass

        preview_collections["main"] = pcoll

    except Exception as e:
        # ถ้ามีปัญหา ให้ remove ทิ้งทันที กัน memory leak
        previews.remove(pcoll)
        raise e

def unregister():
    # ถอดถอนทุก collection ที่เราสร้างไว้
    for key, pcoll in list(preview_collections.items()):
        try:
            previews.remove(pcoll)
        except Exception:
            pass
    preview_collections.clear()
