import bpy
import bmesh
from bpy.types import (Context, Event, Operator)
from bpy.props import (EnumProperty, PointerProperty, StringProperty, FloatVectorProperty, FloatProperty, IntProperty, BoolProperty)

from . import func_core
import math
import random

from ..ui import add_panel, add_expand_panel

class Duckx_OT_UVMapManager(Operator):
    bl_idname = "duckx_tools.uv_map_manager"
    bl_label = "UV Map"
    bl_description = "CLICK for Active UVMaps \nSHIFT CLICK for rename \nCTRL CLICK for New \nALT CLICK for remove UV Map"

    action : StringProperty(name="Action")
    
    old_name: StringProperty()  # เพิ่ม property เก็บชื่อเดิม

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
    
    def invoke(self, context, event):
        action = self.action.split(':>')
        objs = context.selected_objects
        active_object = context.active_object
        if event.shift:
            self.action = f"uvrename:>{action[1]}:>{action[2]}"
            # เก็บชื่อเดิมไว้
            if active_object.data.uv_layers:
                
                target_index = int(action[1])
                self.old_name = context.active_object.data.uv_layers[target_index].name
                for obj in objs:
                    if obj.type == "MESH":
                        obj.data.uv_layers.active_index = target_index
                wm = context.window_manager
                return wm.invoke_props_dialog(self)
            else:
                self.report({'WARNING'}, "UV Is not available")
                return {'CANCELLED'}
        elif event.alt:
            bpy.ops.duckx_tools.delete_uvmap('INVOKE_DEFAULT', action=self.action)
            return self.execute(context)
        elif event.ctrl:
            self.action = "uvnew"
            return self.execute(context)
        else:
            return self.execute(context)
        
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        uvmaps = context.active_object.data.uv_layers
        for uvmap in uvmaps:
            if context.active_object.data.uv_layers.active.name == uvmap.name:
                row.prop(uvmap, "name", text="")
        
    
    def execute(self, context):
        action = self.action.split(':>')
        objs = context.selected_objects
        active_object = context.active_object
        print(action)

        if action[0] == "uvactive":
            for obj in objs:
                if obj.type == "MESH":
                    obj.data.uv_layers.active_index = int(action[1])
                    for uv_layer in obj.data.uv_layers:
                        if uv_layer.name == action[2]:
                            uv_layer.active_render = True
                            break
        
        elif action[0] == "uvnew":
            if len(active_object.data.uv_layers) == 8:
                self.report({'WARNING'}, "Cannot add more than 8 UV maps")
                return {'CANCELLED'}  # ไม่สามารถสร้าง UV Map ใหม่ได้ถ้ามีมากกว่า 8
            for obj in objs:
                if obj.type == "MESH":
                    new_uv_layer = obj.data.uv_layers.new(name=f"UV{len(obj.data.uv_layers)+1}")
                    obj.data.uv_layers.active = new_uv_layer
                    print(f"New UV Map created: {new_uv_layer.name}")
        
        elif action[0] == "uvrename":
            # เก็บชื่อ UV Map ของ uv_layer ที่ active อยู่
            new_name = active_object.data.uv_layers.active.name  # เพิ่ม .name ตรงนี้
            target_index = int(action[1])
            for obj in objs:
                if obj.type == "MESH":
                    if len(obj.data.uv_layers) > target_index:
                        obj.data.uv_layers[target_index].name = new_name
                        print(f"UV Map at index {target_index} renamed to: {new_name}")

        
        obj = bpy.context.active_object
        bpy.data.objects[obj.name].select_set(True)
        return {'FINISHED'}
    
    def cancel(self, context):
        # เมื่อกด cancel ให้คืนค่าชื่อเดิม
        action = self.action.split(':>')
        target_index = int(action[1])
        objs = context.selected_objects
        for obj in objs:
            if obj.type == "MESH":
                if len(obj.data.uv_layers) > target_index:
                    obj.data.uv_layers[target_index].name = self.old_name
        return None
    
class Duckx_OT_DeleteUVMap(bpy.types.Operator):
    bl_idname = "duckx_tools.delete_uvmap"
    bl_label = "Delele UV Map by Name"
    bl_options = {'REGISTER', 'UNDO'}

    action : StringProperty(name="Action")

    def invoke(self, context, event):
        # เรียก popup ยืนยัน
        return context.window_manager.invoke_confirm(self, event)
    
    def execute(self, context):
        action = self.action.split(':>')
        objs = context.selected_objects
        print("Deleting UV Map:", action)
        for obj in objs:
            if obj.type == "MESH":
                for uv_layer in obj.data.uv_layers:
                    if uv_layer.name == action[2]:
                        obj.data.uv_layers.remove(uv_layer)
        obj = bpy.context.active_object
        bpy.data.objects[obj.name].select_set(True)
        return {'FINISHED'}
    
class Duckx_OT_InvertSeam(Operator):
    bl_idname = "duckx_tools.invert_seam"
    bl_label = "Invert Seam"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_icon = "SHADERFX"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Invert UV seam from edge selected"

    @classmethod
    def poll(cls, context):
        return (context.object is not None and 
                context.object.type == 'MESH' and 
                context.mode == 'EDIT_MESH')

    def execute(self, context):
        obj = context.edit_object
        me = obj.data

        bm = bmesh.from_edit_mesh(me)
        bm.faces.ensure_lookup_table()  # Ensure face data is updated

        for edge in bm.edges:
            if edge.select:
                edge.seam = not edge.seam
                

        bmesh.update_edit_mesh(me)
        return {'FINISHED'}
    
class Duckx_OT_UVRotation(Operator):
    bl_idname = "duckx_tools.uv_rotation"
    bl_label = "UV Rotation"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_icon = "SHADERFX"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "[SHIFT CLICK] for rotate only selected"

    angle : FloatProperty(name="Angle")
    islands = True

    @classmethod
    def poll(cls, context):
        return (context.object is not None and 
                context.object.type == 'MESH' and 
                context.mode == 'EDIT_MESH')    

    def invoke(self, context, event):
        if event.shift:
            self.islands = False
            return self.execute(context)
        else:
            return self.execute(context)
                
    def execute(self, context):
        if not context.area.type == 'IMAGE_EDITOR':
            angle = self.angle * -1
            
            
            if not self.islands:
                func_core.move_selected_uv(0.000001, 0.000001)
                func_core.rotate_selected_uv_island(angle)
            else:
                avg_u, avg_v = func_core.get_active_uv_island_position()
                func_core.rotate_selected_uv_island(angle)
                func_core.move_selected_uv_island(avg_u, avg_v)
        else:
            angle = self.angle
            
            if bpy.context.scene.tool_settings.use_uv_select_sync == True:
                uvSync = True
            else:
                uvSync = False
            
            if not context.area.type == 'IMAGE_EDITOR':
                bpy.context.area.ui_type = 'UV'
                bpy.context.scene.tool_settings.use_uv_select_sync = False
                bpy.ops.uv.select_all(action='SELECT')
                space_data = context.space_data
                current_pivot_point = space_data.pivot_point
                space_data.pivot_point = 'CENTER'
                bpy.ops.transform.rotate(value=math.radians(angle), use_proportional_edit=False)
                space_data.pivot_point = current_pivot_point
                bpy.context.area.ui_type = 'VIEW_3D'
            else:
                bpy.ops.transform.rotate(value=math.radians(angle), use_proportional_edit=False)
            
            if uvSync == True:
                bpy.context.scene.tool_settings.use_uv_select_sync = True
            else:
                bpy.context.scene.tool_settings.use_uv_select_sync = False
        self.hold_shift = False
        return {'FINISHED'}

class Duckx_OT_UVPositionRandom(Operator):
    bl_idname = "duckx_tools.uv_position_random"
    bl_label = "UV Random Position"
    bl_icon = "UV"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Random UV Island Position \nSHIFT CLICK for Random selected only"

    action : EnumProperty(
        name = "Property",
        items = [('x', "X", ""),
                 ('y', "Y", "")
                 ]
    )
    islands = True

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH' and context.tool_settings.mesh_select_mode[2]
    
    def invoke(self, context, event):
        if event.shift:
            self.islands = False
            return self.execute(context)
        else:
            return self.execute(context)
    
    def execute(self, context):
        x, y = func_core.get_active_uv_island_position()
        if self.action == "x":
            #bpy.ops.uv.randomize_uv_transform(loc=(1, 0))
            if not self.islands:
                func_core.move_selected_uv(random.uniform(-1, 1), 0)
            else:
                func_core.move_selected_uv_island(random.uniform(-1, 1), y)
        elif self.action == "y":
            if not self.islands:
                func_core.move_selected_uv(x, random.uniform(-1, 1))
            else:
                func_core.move_selected_uv_island(x, random.uniform(-1, 1))
            #bpy.ops.uv.randomize_uv_transform(loc=(0, 1))
                
        return {'FINISHED'}

        
def draw_uv_map_manager(self, context, layout, properties):
    active_object = context.active_object
    props = properties
    if active_object and active_object.type == 'MESH':
        box = layout.box()
        row = box.row(align=True)
        uv_active = False
        if active_object.data.uv_layers:
            for i, uv_layer in enumerate(active_object.data.uv_layers):
                if active_object.data.uv_layers.active == uv_layer:
                    uv_active = True
                else:
                    uv_active = False
                if len(active_object.data.uv_layers) < 5:
                    row.operator("duckx_tools.uv_map_manager", text=uv_layer.name, depress=uv_active).action = f"uvactive:>{i}:>{uv_layer.name}"
                else:
                    row.operator("duckx_tools.uv_map_manager", text=str(i+1), depress=uv_active).action = f"uvactive:>{i}:>{uv_layer.name}"
        else:
            row.operator("duckx_tools.uv_map_manager", text="New UV", depress=uv_active).action = f"uvnew:>0:>UV1"

def draw_invert_seam(self, context, layout, properties):
    layout.operator("duckx_tools.invert_seam")

def draw_uv_rotation(self, context, layout, properties):
    box = layout.box()
    row = box.row()
    row.label(text="UV Rotation")
    row.prop(properties, "uv_angle", text="")
    row.operator("duckx_tools.uv_rotation", text="", icon="FILE_REFRESH").angle = properties.uv_angle
    row = box.row()
    row.operator("duckx_tools.uv_rotation", text="-90°").angle = -90
    row.operator("duckx_tools.uv_rotation", text="+90°").angle = 90
    row.operator("duckx_tools.uv_rotation", text="-45°").angle = -45
    row.operator("duckx_tools.uv_rotation", text="+45°").angle = 45
    row = box.row()
    row.operator("duckx_tools.uv_rotation", text="180°").angle = 180

add_panel("UV_Map_Manager", draw_uv_map_manager)
add_panel("Invert Seam", draw_invert_seam)
add_panel("UV Rotation", draw_uv_rotation)
    
def register():
    bpy.utils.register_class(Duckx_OT_UVMapManager)
    bpy.utils.register_class(Duckx_OT_DeleteUVMap)
    bpy.utils.register_class(Duckx_OT_InvertSeam)
    bpy.utils.register_class(Duckx_OT_UVRotation)
    bpy.utils.register_class(Duckx_OT_UVPositionRandom)

        
    
def unregister():
    bpy.utils.unregister_class(Duckx_OT_UVMapManager)
    bpy.utils.unregister_class(Duckx_OT_DeleteUVMap)
    bpy.utils.unregister_class(Duckx_OT_InvertSeam)
    bpy.utils.unregister_class(Duckx_OT_UVRotation)
    bpy.utils.unregister_class(Duckx_OT_UVPositionRandom)

