
bl_info = {
        "name": "DuckX Tools",
        "description": "My awesome add-on.",
        "author": "Kanong Manuree",
        "version": (2, 0),
        "blender": (3, 5, 0),
        "location": "View3D",
        "warning": "", # used for warning icon and text in add-ons panel
        "wiki_url": "",
        "tracker_url": "",
        "support": "COMMUNITY",
        "category": "Object"
        }

import bpy
from bpy.app.handlers import persistent

from . import properties
from . import ui
from . import icon_reg
from .operators import func_core

from .operators import register as reg_operators
from .operators import unregister as unreg_operators


# เรียกใช้ตัวเพิ่มคีย์แมพที่คุณมีอยู่แล้ว (ซึ่งเช็คไม่ให้ซ้ำ)
@persistent
def _duckx_ensure_keymap(_):
    try:
        # ถ้า operator ของคุณอ้างอิง scene props เช่น context.scene.duckx_tools
        # ให้แน่ใจว่า PropertyGroup ถูก register แล้วก่อนจะเรียกใช้
        bpy.ops.duckx_tools.keymap_add()
    except Exception as e:
        print("[DuckX Tools] ensure keymap skipped:", e)


def register():
     properties.register()
     ui.register()
     icon_reg.register()
     reg_operators()

     settings = func_core.read_json("setting.json")
     if settings.get("Keymap Assign", False):
          # ผูก handler ครั้งเดียว
          if _duckx_ensure_keymap not in bpy.app.handlers.load_post:
               bpy.app.handlers.load_post.append(_duckx_ensure_keymap)

          # (ทางเลือก) เรียกทันทีตอนเปิดใช้งานแอดออนด้วย
          try:
               bpy.ops.duckx_tools.keymap_add()
          except Exception as e:
               print("[DuckX Tools] initial keymap add skipped:", e)
     


def unregister():
     properties.unregister()
     ui.unregister()
     icon_reg.unregister()
     unreg_operators()

     if _duckx_ensure_keymap in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_duckx_ensure_keymap)
     

if __name__ == '__main__':
     register()
