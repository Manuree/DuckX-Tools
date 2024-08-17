import bpy
from bpy.types import (Operator)
from bpy.props import (EnumProperty, PointerProperty, StringProperty, FloatVectorProperty, FloatProperty, IntProperty, BoolProperty)

from . import func_core
import math

  
class Duckx_OT_ShowAndHide(Operator):
    bl_idname = "duckx_tools.show_hide_operator"
    bl_label = "Show and Hide"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Show and Hide group objects"

    action : StringProperty(name="Action")
    index : IntProperty(name="Index")
    #lable : StringProperty(name="Lable")
    hide_all = True
    
    def invoke(self, context, event):
        if event.shift:
            self.hide_all = False
            return self.execute(context)
        else:
            return self.execute(context)
    
    def execute(self, context):
        scene = context.scene
        duckx_tools = scene.duckx_tools
        action = self.action
        index = self.index
        #lable = self.lable

        list_groups = func_core.string_to_list(duckx_tools.list_groups)
        obj_list = []
        if action == "add":
            print("Add to group")
            objs = context.selected_objects
            for obj in objs:
                list_groups[index].append(obj.name)
            list_groups[index] = list(set(list_groups[index]))
        elif action == "remove":
            print("Remove from group")
            objs = context.selected_objects
            for obj in objs:
                if obj.name in list_groups[index]:
                    list_groups[index].remove(obj.name)
        elif action == "show":
            print("Show group")
            print(list_groups[index])
            
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except:
                pass
            
            if self.hide_all:
                bpy.ops.object.select_all(action='SELECT')
                bpy.ops.object.hide_view_set(unselected=False)
                
            
            for name in list_groups[index]:
                if name in bpy.data.objects:
                    obj = bpy.data.objects.get(name)
                    bpy.context.view_layer.objects.active = obj
                    obj.hide_set(False)
                else:
                    print(name + " is gone")
                
            # bpy.context.area.ui_type = 'OUTLINER'
            # bpy.ops.outliner.select_all()
            # bpy.ops.outliner.unhide_all()
            # bpy.context.area.ui_type = 'VIEW_3D'
            # bpy.ops.object.hide_view_clear()
            
            func_core.select_objects_by_name(list_groups[index])
            func_core.focus_object_in_outliner()
            bpy.ops.object.select_all(action='DESELECT')

            
            # bpy.ops.object.hide_view_set(unselected=True)
            # bpy.ops.object.select_all(action='DESELECT')
        elif action == "append":
            print("Append new group")
            objs = context.selected_objects
            for obj in objs:
                obj_list.append(obj.name)
            list_groups.append(obj_list)
        elif action == "del":
            print("Delete group")
            del list_groups[index]

        duckx_tools.list_groups = func_core.list_to_string(list_groups)
        #duckx_tools.list_groups = ""
        
        return {'FINISHED'}
    
def register():
    bpy.utils.register_class(Duckx_OT_ShowAndHide)

        
    
def unregister():
    bpy.utils.unregister_class(Duckx_OT_ShowAndHide)

