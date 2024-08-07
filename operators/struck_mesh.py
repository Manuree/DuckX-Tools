import bpy
import math

from . import func_core

from bpy.types import (Operator )
from bpy.props import (EnumProperty, PointerProperty, StringProperty, FloatVectorProperty, FloatProperty, IntProperty, BoolProperty)

class Duckx_OT_DuplicateBlend(Operator):
    bl_idname = "duckx_tools.duplicate_blend_operator"
    bl_label = "Duplicate Blend"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_icon = "MOD_ARRAY"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Duplicate mesh between active mesh"
    
    num : IntProperty(name="Number Between", default=1, min=1) # type: ignore
    rotation : BoolProperty(name="With Rotation", default=True) # type: ignore
    dimention : BoolProperty(name="With Dimention",default=True) # type: ignore
    
    def execute(self, context):
        num = self.num + 1
        lo : FloatVectorProperty(name="Object Location") # type: ignore
        di : FloatVectorProperty(name="Object Dimensions") # type: ignore
        selected_objects = bpy.context.selected_objects
        active_object = bpy.context.active_object
        if len(selected_objects) == 2:
            selected_objects.remove(active_object)
            for obj in selected_objects:
                step =1
                loc_x = func_core.blend_numbers(obj.location.x, active_object.location.x, num+1)
                loc_y = func_core.blend_numbers(obj.location.y, active_object.location.y, num+1)
                loc_z = func_core.blend_numbers(obj.location.z, active_object.location.z, num+1)
                loc_x = loc_x[1:-1]
                loc_y = loc_y[1:-1]
                loc_z = loc_z[1:-1]
                ro_x = func_core.blend_numbers(obj.rotation_euler.x, active_object.rotation_euler.x, num+1)
                ro_y = func_core.blend_numbers(obj.rotation_euler.y, active_object.rotation_euler.y, num+1)
                ro_z = func_core.blend_numbers(obj.rotation_euler.z, active_object.rotation_euler.z, num+1)
                ro_x = ro_x[1:-1]
                ro_y = ro_y[1:-1]
                ro_z = ro_z[1:-1]
                di_x = func_core.blend_numbers(obj.dimensions.x, active_object.dimensions.x, num+1)
                di_y = func_core.blend_numbers(obj.dimensions.y, active_object.dimensions.y, num+1)
                di_z = func_core.blend_numbers(obj.dimensions.z, active_object.dimensions.z, num+1)
                di_x = di_x[1:-1]
                di_y = di_y[1:-1]
                di_z = di_z[1:-1]
                for i in range(self.num):
                    bpy.ops.object.select_all(action='DESELECT')
                    obj.select_set(True)
                    bpy.context.view_layer.objects.active = obj
                    bpy.ops.object.duplicate_move_linked()
                    #bpy.ops.transform.translate(value=(active_object.location.x/num*step, active_object.location.y/num*step, active_object.location.z/num*step))
                    selectObject = bpy.context
                    selectObject.object
                    loc = [loc_x[i], loc_y[i], loc_z[i]]
                    bpy.context.object.location = loc
                    if self.rotation:
                        # bpy.context.active_object.rotation_euler.x = active_object.rotation_euler.x/num*step
                        # bpy.context.active_object.rotation_euler.y = active_object.rotation_euler.y/num*step
                        # bpy.context.active_object.rotation_euler.z = active_object.rotation_euler.z/num*step
                        ro = [ro_x[i], ro_y[i], ro_z[i]]
                        bpy.context.object.rotation_euler = ro
                    if self.dimention:
                        #bpy.context.active_object.dimensions.x = di_x[i]
                        di = [di_x[i], di_y[i], di_z[i]]
                        bpy.context.object.dimensions = di
                    step += 1
        else:
            self.report({"INFO"} ,"Please Select Two Objects")
        return {'FINISHED'}

class Duckx_OT_SetMeshName(Operator):
    bl_idname = "duckx_tools.set_mesh_name_operator"
    bl_label = "Set Mesh Name"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_icon = "MESH_DATA"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Rename Mesh Data"

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
        selected_objects = context.selected_objects
        scene = context.scene
        duckx_tools = scene.duckx_tools
        
        if duckx_tools.name_to_mesh == True:
            for obj in selected_objects:
                print(obj.data.name)
                print(obj.name)
                if obj.type == 'MESH' or obj.type == 'CURVE':
                    obj.data.name = obj.name
        else:
            for obj in selected_objects:
                print(obj.data.name)
                print(obj.name)
                if obj.type == 'MESH' or obj.type == 'CURVE':
                    obj.name = obj.data.name
        print(obj.data.name)
        print(obj.name)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(Duckx_OT_DuplicateBlend)
    bpy.utils.register_class(Duckx_OT_SetMeshName)
           
def unregister():
    bpy.utils.unregister_class(Duckx_OT_DuplicateBlend)
    bpy.utils.unregister_class(Duckx_OT_SetMeshName)
        
