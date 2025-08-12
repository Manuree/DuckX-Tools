import os
import importlib
import inspect

# Get the current directory
current_dir = os.path.dirname(__file__)

# Dictionary to store all functions
all_functions = {}

# Find all .py files in the current directory
for file in os.listdir(current_dir):
    if file.endswith('.py') and not file.startswith('__'):
        # Get module name without .py
        module_name = file[:-3]
        
        # Import the module
        module = importlib.import_module(f'.{module_name}', package=__package__)
        
        # Get all functions from the module 
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj):
                # Add function to dictionary and make it available
                all_functions[name] = obj
                globals()[name] = obj

# Create __all__ list
__all__ = list(all_functions.keys())