import bpy
import os
import bpy.utils.previews


def iconLib(name="duckx_icon"):
    pcoll = preview_collections["main"]
    icon = pcoll[name]
    return(icon.icon_id)

preview_collections = {}

def register():
    pcoll = bpy.utils.previews.new()

    # path to the folder where the icon is
    # the path is calculated relative to this py file inside the addon folder
    icon_path = os.path.join(os.path.dirname(__file__), "icons")
    for entry in os.scandir(icon_path):
        if entry.name.endswith(".png"):
            name = os.path.splitext(entry.name)[0]
            pcoll.load(name, os.path.join(icon_path, entry.name), 'IMAGE')

    preview_collections["main"] = pcoll



def unregister():
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)

    preview_collections.clear()