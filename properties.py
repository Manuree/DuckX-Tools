import bpy

from bpy.types import Scene
from bpy.types import (PropertyGroup)
from bpy.props import (EnumProperty, PointerProperty, StringProperty, FloatVectorProperty, FloatProperty, IntProperty, BoolProperty)



class MyProperties(PropertyGroup):
    tabs_menu : EnumProperty(
        name = "Tabs",
        items = [('mesh', "Mesh", "Tools for mesh", "FACE_MAPS", 1),
                 ('uv', "UV", "Tools for UV", "UV", 2),
                 ('anim', "Animetion", "Tools for Animation", "ARMATURE_DATA", 3),
                 ('macro', "Macro", "Macro Tools", "SEQ_STRIP_META", 4),
                 ('view', "View", "Tools for view and display", "WORKSPACE", 5),
                 ('render', "Render", "Tools for Render", "OUTPUT", 6),
                 ('setting', "Setting", "Addon setting", "PREFERENCES", 7)
                 ]
    )

    auto_keymap : BoolProperty(name="Auto Assign Keymap Toggle", default=True)
    tri_count : BoolProperty(name="Triangles count", default=False)
    tri_track : BoolProperty(name="Triangles tracker", default=False)
    uvmap_active : BoolProperty(name="UV Map active", default=True)
    flip_tools_toggle : BoolProperty(name="Flip Tools Toggle", default=False)
    object_data : BoolProperty(name="Object Data Toggle", default=False)
    shape_tools : BoolProperty(name="Shape Tools Toggle", default=False)
    mesh_data : BoolProperty(name="Mesh Data Tools Toggle", default=False)
    modifiers_tools : BoolProperty(name="Modifiers Tools Toggle", default=False)
    merge_tools : BoolProperty(name="Merge Tools Toggle", default=False)
    movex_tools : BoolProperty(name="Merge Tools Toggle", default=False)
    show_hide_panel : BoolProperty(name="Show & Hide Panel", default=True)
    decals_panel : BoolProperty(name="Decals Panel", default=False)

    obj_color : FloatVectorProperty(name="Color", subtype='COLOR', size=4, min=0, max=1, default=(0.0, 0.0, 0.0, 1.0),)
    name_to_mesh : BoolProperty(name="Mesh Data Name Tools Toggle", default=True)
    uvmap_set_type : EnumProperty(
        name = "Type",
        items = [('name', "Name", ""),
                 ('index', "Index", "")
                 ]
    )
    uvmap_name : StringProperty(name="UV Map Name")
    uvmap_index : IntProperty(name="UV Map Index", min=1, default=1)
    uv_angle : FloatProperty(name="UV Angle", step=1, default=0.0, precision=2)

    #Show and Hide Tools
    list_groups : StringProperty(name="List Group")

    #Modifiers Tools
    mod_name : StringProperty(name="Modifiers Name")

    #Triangles Tools
    tri_cal_factor : FloatProperty(name="Triangle Calculator Factor", step=1, default=0.5, precision=2)
    tri_sum : StringProperty(name="Triangles Summary")

    #Decals Tools
    decal_ring_set : BoolProperty(name="Ring Decal Setting", default=False)
    decal_ring_mat : PointerProperty(type=bpy.types.Material, description="Material Assign to Ring Decal")

classes = [MyProperties]
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    Scene.duckx_tools = PointerProperty(type= MyProperties)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del Scene.duckx_tools