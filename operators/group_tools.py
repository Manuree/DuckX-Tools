import bpy
from bpy.types import (Operator)
from bpy.props import (EnumProperty, PointerProperty, StringProperty, FloatVectorProperty, FloatProperty, IntProperty, BoolProperty)

from . import func_core
import math


edit_tab_name = False
dummy_data = [["collection", ["A", "B", "C"]], ["object", ["D", "E", "F"]]]
  

class Duckx_OT_GroupTools(Operator):
    bl_idname = "duckx_tools.group_tools_operator"
    bl_label = "Group Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Show and Hide group objects"

    action : StringProperty(name="Action")
    tab_index : IntProperty(name="Tab Index")
    index : IntProperty(name="Index")
    hide_all = True
    invert = False
    select = False
    move = False
    
    def invoke(self, context, event):
        if event.shift:
            if event.ctrl:
                self.select = True
            self.hide_all = False
            return self.execute(context)
        elif event.ctrl and event.alt:
            self.move = True
            return self.execute(context)
        elif event.alt:
            self.invert = True
            return self.execute(context)
        elif event.ctrl:
            self.select = True
            return self.execute(context)
        else:
            return self.execute(context)
    
    def draw(self, context):
        layout = self.layout
    
    def execute(self, context):
        scene = context.scene
        duckx_tools = scene.duckx_tools
        action = self.action
        index = self.index
        tab_index = self.tab_index
        global edit_tab_name

        group_lib = func_core.string_to_list(duckx_tools.group_lib)
        #print(action)
        # Tab Action
        if action == "add_tab":
            group_lib.append(["Untitled "+str(len(group_lib)), []])
            duckx_tools.tab_active = len(group_lib) - 1
            print(f"{action} : {str(group_lib)}")
            print(f"tab_active : {duckx_tools.tab_active}")
        elif action == "del_tab":
            print(f"{action} : {str(duckx_tools.tab_active)}")
            del group_lib[duckx_tools.tab_active]
            duckx_tools.tab_active = duckx_tools.tab_active - 1
        elif action == "active_tab":
            duckx_tools.tab_active = tab_index
            print(f"{action} : {str(duckx_tools.tab_active)}")
        elif action == "rename_tab":
            edit_tab_name = True
            duckx_tools.group_tab_name = group_lib[duckx_tools.tab_active][0]
            print(f"{action} : {str(duckx_tools.tab_active)}")
        elif action == "rename_yes":
            group_lib[duckx_tools.tab_active][0] = duckx_tools.group_tab_name
        elif action == "rename_cancel":
            edit_tab_name = False
            return {'FINISHED'}
        
        # Group Action
        elif action == "add_coll_group":
            active_collection = bpy.context.view_layer.active_layer_collection
            collection_name = active_collection.name
            new_group = ["collection",[collection_name]]
            group_lib[duckx_tools.tab_active][1].append(new_group)
            func_core.message_box("Added a Collection to group", "Group Added", "INFO")

            # Work inprogress
            #selected_collections = []
            # for collection in bpy.data.collections:
            #     for obj in collection.objects:
            #         if obj.select_get():
            #             selected_collections.append(collection.name)
            #             break
        elif action == "add_obj_group":
            objs = context.selected_objects
            if len(objs) > 0:
                new_group = ["object",[]]
                for obj in objs:
                    new_group[1].append(obj.name)
                group_lib[duckx_tools.tab_active][1].append(new_group)
                func_core.message_box("Added objects to group", "Group Added", "INFO")
            else:
                return {'FINISHED'}
        elif action == "active_group":
            print("Show group")
            if group_lib[duckx_tools.tab_active][1][index][0] == "collection":
                collection_name = group_lib[duckx_tools.tab_active][1][index][1][0]
                if self.move:
                    print("Move to group")
                    # ตรวจสอบว่าคอลเลคชันมีอยู่จริง
                    collection = bpy.data.collections.get(collection_name)
                    if not collection:
                        print(f"Collection '{collection_name}' does not exist!")
                    else:
                        # วัตถุที่เลือกในปัจจุบัน
                        selected_objects = bpy.context.selected_objects

                        for obj in selected_objects:
                            # ลบวัตถุออกจากคอลเลคชันปัจจุบันทั้งหมด
                            for obj_collection in obj.users_collection:
                                obj_collection.objects.unlink(obj)

                            # ลิงก์วัตถุไปยังคอลเลคชันเป้าหมาย
                            collection.objects.link(obj)

                        print(f"Moved {len(selected_objects)} object(s) to collection '{collection_name}'.")
                    return {'FINISHED'}
                try:
                    bpy.ops.object.mode_set(mode='OBJECT')
                except:
                    pass
                bpy.ops.object.hide_view_clear()
                bpy.ops.object.select_all(action='DESELECT')
                collection = bpy.data.collections.get(collection_name)
                hierarchy_collections = func_core.get_hierarchy_collections(collection)
                if self.hide_all:
                    for coll in bpy.data.collections:
                        if not coll.name in hierarchy_collections:
                            func_core.hide_collection(coll.name, True)
                        else:
                            func_core.hide_collection(coll.name, False)
                else:
                    for coll in bpy.data.collections:
                        if coll.name in hierarchy_collections:
                            func_core.hide_collection(coll.name, False)
                #print(func_core.get_all_related_collections(collection_name))

                func_core.hide_collection(collection_name, False)
                if self.select:
                    func_core.select_objects_in_collection(collection_name)
                func_core.focus_object_in_outliner()
            else:
                for coll in bpy.data.collections:
                    func_core.hide_collection(coll.name, False)
                objs = group_lib[duckx_tools.tab_active][1][index][1]
                print(objs)
                
                try:
                    bpy.ops.object.mode_set(mode='OBJECT')
                except:
                    pass
                
                bpy.ops.object.select_all(action='DESELECT')
                if self.hide_all:
                    bpy.ops.object.hide_view_set(unselected=True)
                bpy.ops.object.select_all(action='SELECT')
                for obj in bpy.context.scene.objects:
                    if obj.name in objs:
                        if self.invert:
                            obj.hide_set(True)
                        else:
                            obj.hide_set(False)
                        obj.select_set(True)
                        bpy.context.view_layer.objects.active = obj
                    
                # bpy.ops.object.hide_view_clear()

                # for name in objs:
                #     if name in bpy.data.objects:
                #         obj = bpy.data.objects.get(name)
                #         bpy.context.view_layer.objects.active = obj
                #         if self.invert:
                #             obj.hide_set(True)
                #         else:
                #             obj.hide_set(False)
                #     else:
                #         print(name + " is gone")

                bpy.ops.object.select_all(action='DESELECT')
                if self.select:
                    func_core.select_objects_by_name(objs)
                func_core.focus_object_in_outliner()
        elif action == "append_to_group":
            objs = context.selected_objects
            if len(objs) > 0:
                for obj in objs:
                    group_lib[duckx_tools.tab_active][1][index][1].append(obj.name)
                group_lib[duckx_tools.tab_active][1][index][1] = list(set(group_lib[duckx_tools.tab_active][1][index][1]))
                group_lib[duckx_tools.tab_active][1][index][1] = sorted(set(group_lib[duckx_tools.tab_active][1][index][1]))
            else:
                return {'FINISHED'}
        elif action == "remove_from_group":
            objs = context.selected_objects
            if len(objs) > 0:
                for obj in objs:
                    if obj.name in group_lib[duckx_tools.tab_active][1][index][1]:
                        group_lib[duckx_tools.tab_active][1][index][1].remove(obj.name)
                    else:
                        return {'FINISHED'}
                group_lib[duckx_tools.tab_active][1][index][1] = list(set(group_lib[duckx_tools.tab_active][1][index][1]))
                group_lib[duckx_tools.tab_active][1][index][1] = sorted(set(group_lib[duckx_tools.tab_active][1][index][1]))
        elif action == "del_group":
            del group_lib[duckx_tools.tab_active][1][index]
            

        if not action == "rename_tab":
            edit_tab_name = False
        duckx_tools.group_lib = func_core.list_to_string(group_lib)
        func_core.refresh_panel()
        return {'FINISHED'}
        
    
def register():
    bpy.utils.register_class(Duckx_OT_GroupTools)

        
    
def unregister():
    bpy.utils.unregister_class(Duckx_OT_GroupTools)

