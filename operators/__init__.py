# from . import add_empty
# from . import orientation
# from . import uv_utilities
# from . import flip_tools
# from . import utilities
# from . import objects_tools
# from . import merge_tools
# from . import struck_mesh
# from . import show_hide_tools
# from . import modifiers_utilities
# from . import triangles_tools
# from . import decals_tools

# def register():
#     add_empty.register()
#     orientation.register()
#     uv_utilities.register()
#     flip_tools.register()
#     utilities.register()
#     objects_tools.register()
#     merge_tools.register()
#     struck_mesh.register()
#     show_hide_tools.register()
#     modifiers_utilities.register()
#     triangles_tools.register()
#     decals_tools.register()


# def unregister():
#     add_empty.unregister()
#     orientation.unregister()
#     uv_utilities.unregister()
#     flip_tools.unregister()
#     utilities.unregister()
#     objects_tools.unregister()
#     merge_tools.unregister()
#     struck_mesh.unregister()
#     show_hide_tools.unregister()
#     modifiers_utilities.unregister()
#     triangles_tools.unregister()
#     decals_tools.unregister()

import os
import importlib

# Get the directory of the current file (__init__.py)
current_dir = os.path.dirname(__file__)

# List all Python files in the directory except __init__.py
module_files = [f[:-3] for f in os.listdir(current_dir) if f.endswith('.py') and f != '__init__.py']

# Import all modules dynamically
modules = [importlib.import_module(f".{module}", package=__name__) for module in module_files]

def register():
    for module in modules:
        if hasattr(module, 'register'):
            module.register()

def unregister():
    for module in modules:
        if hasattr(module, 'unregister'):
            module.unregister()
