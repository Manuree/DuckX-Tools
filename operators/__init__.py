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
