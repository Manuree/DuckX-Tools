import bpy
import math

from . import func_core

from bpy.types import (Operator )
from bpy.props import (EnumProperty, PointerProperty, StringProperty, FloatVectorProperty, FloatProperty, IntProperty, BoolProperty)


objects = []
tracking = False

class Duckx_OT_TrianglesCal(Operator):
    bl_idname = "duckx_tools.tri_cal_operator"
    bl_label = "Triangles Calculator"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_icon = "CON_TRANSLIKE"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Calculator Triangles"

    @classmethod
    def poll(cls, context):
        selected_objects = context.selected_objects
        
        # Check if any objects are selected
        if not selected_objects:
            return False 

        # Check if the active object is a mesh or a curve
        active_object = context.active_object
        if active_object and (active_object.type == 'MESH' or active_object.type == 'CURVE'):
            return True
        
        return False

    def execute(self, context):
        scene = context.scene
        duckx_tools = scene.duckx_tools 
        duckx_tools.tri_sum = str(math.floor(func_core.get_triangle() * duckx_tools.tri_cal_factor))
        print(duckx_tools)
        return {'FINISHED'}
    
class Duckx_OT_TrianglesTracker(Operator):
    bl_idname = "duckx_tools.tri_tracker_operator"
    bl_label = "Triangles Calculator"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_icon = "CON_TRANSLIKE"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Tracking Triangles"

    select_mode = False
    def invoke(self, context, event):
        if event.shift:
            self.select_mode = True
            return self.execute(context)
        else:
            return self.execute(context)

    def execute(self, context):
        global objects, tracking
        selected_objects = context.selected_objects
        if self.select_mode:
            for obj in objects:
                print(obj)
                func_core.select_object_by_name(obj[0])
        else:
            objects.clear()
            for obj in selected_objects:
                bpy.ops.object.select_all(action='DESELECT')
                if obj.type == "MESH":
                    func_core.select_object_by_name(obj.name)
                    objects.append([obj.name, func_core.get_triangle()])
            print(objects)
            if tracking == False and objects != []:
                tracking = True
            else:
                tracking = False
            for obj in selected_objects:
                obj.select_set(True)
        return {'FINISHED'}

def register():
    bpy.utils.register_class(Duckx_OT_TrianglesCal)
    bpy.utils.register_class(Duckx_OT_TrianglesTracker)
           
def unregister():
    bpy.utils.unregister_class(Duckx_OT_TrianglesCal)
    bpy.utils.unregister_class(Duckx_OT_TrianglesTracker)
        
