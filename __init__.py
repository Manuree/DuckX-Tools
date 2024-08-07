
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

from . import properties
from . import ui
from . import icon_reg
from . import setting

from .operators import func_core
from .operators import register as reg_operators
from .operators import unregister as unreg_operators

#Check patch version
addon_version = bl_info["version"]
addon_version_string = ".".join(map(str, addon_version))




def register():
     properties.register()
     ui.register()
     icon_reg.register()
     setting.register()
     func_core.addon_version = addon_version_string
     reg_operators()
     


def unregister():
     properties.unregister()
     ui.unregister()
     icon_reg.unregister()
     setting.unregister()
     unreg_operators()
     

if __name__ == '__main__':
     register()
