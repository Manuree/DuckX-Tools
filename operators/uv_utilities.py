import bpy
from bpy.types import (Context, Event, Operator)
from bpy.props import (EnumProperty, PointerProperty, StringProperty, FloatVectorProperty, FloatProperty, IntProperty, BoolProperty)

from . import func_core
import math
import random

class Duckx_OT_ActiveUVMap(Operator):
    bl_idname = "duckx_tools.active_uv_map_operator"
    bl_label = "UV Map"
    bl_description = "CLICK for Active UVMaps \nSHIFT CLICK for rename \nCTRL CLICK for New \nALT CLICK for remove UV Map"

    action : StringProperty(name="Action")
    edit = False
    
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
        parts = self.action.split(':>')
        objs = context.selected_objects
        if event.shift and "duckx_uvset:>" in self.action:
            self.edit = True
            for obj in objs:
                if obj.type == "MESH":
                    obj.data.uv_layers.active_index = int(parts[1])
                    for uv_layer in obj.data.uv_layers:
                        if uv_layer.name == parts[2]:
                            uv_layer.active_render = True
                            break
            wm = context.window_manager
            return wm.invoke_props_dialog(self)
        elif event.alt and "duckx_uvset:>" in self.action:
            for obj in objs:
                if obj.type == "MESH":
                    for uv_layer in obj.data.uv_layers:
                        if uv_layer.name == parts[2]:
                            obj.data.uv_layers.remove(uv_layer)
            return self.execute(context)
        elif event.ctrl and "duckx_uvset:>" in self.action:
            self.action = "new"
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
        action = self.action
        scene = context.scene
        duckx_tools = scene.duckx_tools
        
        if action == "toggle":
            objs = context.selected_objects
            if objs:
                for obj in objs:
                    if obj.type == "MESH":
                        uv_layer = obj.data.uv_layers.active
                        if uv_layer:
                            obj.data.uv_layers.active_index = (obj.data.uv_layers.active_index + 1) % len(obj.data.uv_layers)
        elif action == "set":
            for ob in context.selected_objects:
                if ob.type == "MESH":
                    if duckx_tools.uvmap_set_type == "index":
                        if len(ob.data.uv_layers) < duckx_tools.uvmap_index:
                            continue
                        ob.data.uv_layers.active_index = duckx_tools.uvmap_index - 1
                    if duckx_tools.uvmap_set_type == "name":
                        for uv_layer in ob.data.uv_layers:
                            if uv_layer.name == duckx_tools.uvmap_name:
                                uv_layer.active = True
                                break
        elif "duckx_uvset:>" in action:
            parts = action.split(':>')
            print(parts[2])
            objs = context.selected_objects
            if not self.edit:
                for obj in objs:
                    if obj.type == "MESH":
                        obj.data.uv_layers.active_index = int(parts[1])
                        for uv_layer in obj.data.uv_layers:
                            if uv_layer.name == parts[2]:
                                uv_layer.active_render = True
                                break
            elif self.edit:
                for obj in objs:
                    if obj.type == "MESH":
                        obj.data.uv_layers.active.name = context.active_object.data.uv_layers.active.name
 
        elif action == "new":
            for ob in context.selected_objects:
                if ob.type == "MESH":
                    ob.data.uv_layers.new(name=duckx_tools.uvmap_name)
                    ob.data.uv_layers.active_index = len(ob.data.uv_layers) - 1
        elif action == "rename" and duckx_tools.uvmap_set_type == "name":
            for ob in context.selected_objects:
                if ob.type == "MESH":
                    current_layer = ob.data.uv_layers.active_index
                    ob.data.uv_layers.active_index = duckx_tools.uvmap_index - 1
                    ob.data.uv_layers.active.name = duckx_tools.uvmap_name
                    ob.data.uv_layers.active_index = current_layer
        elif action == "del":
            ob = context.active_object
            for ob in context.selected_objects:
                if ob.type == "MESH":
                    if duckx_tools.uvmap_set_type == "index":
                        if len(ob.data.uv_layers) >= duckx_tools.uvmap_index:
                            ob.data.uv_layers.remove(ob.data.uv_layers[duckx_tools.uvmap_index - 1])
                    if duckx_tools.uvmap_set_type == "name":
                        for uv_layer in ob.data.uv_layers:
                            if uv_layer.name == duckx_tools.uvmap_name:
                                ob.data.uv_layers.remove(uv_layer)
                                break
            pass
        
        obj = bpy.context.active_object
        bpy.data.objects[obj.name].select_set(True)
        return {'FINISHED'}
    
class Duckx_OT_UvRotation(Operator):
    bl_idname = "duckx_tools.uvrotation_operator"
    bl_label = "UV Rotation"
    #bl_icon = "MOD_EXPLODE"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Rotation UV \nSHIFT CLICK for rotate from selected face"

    angle : FloatProperty(name="Angle")
    islands = True
    
    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

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

    # def modal(self, context, event):
    #     if event.type == 'LEFTMOUSE' and event.value == 'PRESS' and event.shift:
    #         # Your operator's main logic here
    #         print("Shift + Left Click detected!")
    #         # Add your code to perform actions here

    #         # Optional: End the operator after execution
    #         return {'FINISHED'} 

    #     elif event.type in {'RIGHTMOUSE', 'ESC'}:
    #         # Cancel the operator if right-clicked or Esc is pressed
    #         return {'CANCELLED'}

    #     # Keep the operator running in the background
    #     return {'RUNNING_MODAL'}

    # def invoke(self, context, event):
    #     # Start the operator in modal mode
    #     context.window_manager.modal_handler_add(self)
    #     return {'RUNNING_MODAL'}

class Duckx_OT_UVPadding(Operator):
    bl_idname = "duckx_tools.uvpadding_operator"
    bl_label = "Padding"
    bl_icon = "MOD_EXPLODE"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Make UV Padding"

    action : EnumProperty(
        name = "Property",
        items = [('more', "More", ""),
                 ('less', "Less", "")
                 ]
    )
    factor : IntProperty(name="Factor", min=1, default=1)
    

    def execute(self, context):
        bpy.context.area.ui_type = 'UV'
        bpy.context.scene.tool_settings.use_uv_select_sync = False
        if self.action == "more":
            for i in range(self.factor) :
                bpy.context.space_data.pivot_point = 'CENTER'
                scale = 1.01
                bpy.ops.transform.resize(value=(scale, scale, scale))
                bpy.context.space_data.pivot_point = 'INDIVIDUAL_ORIGINS'
                scale = 0.9900990099009901
                bpy.ops.transform.resize(value=(scale, scale, scale))
                #bpy.ops.transform.translate(value=(-0.0033333, -0.0033333, 0), orient_type='GLOBAL')
        elif self.action == "less":
            for i in range(self.factor) :
                bpy.context.space_data.pivot_point = 'CENTER'
                scale = 0.9900990099009901
                bpy.ops.transform.resize(value=(scale, scale, scale))
                bpy.context.space_data.pivot_point = 'INDIVIDUAL_ORIGINS'
                scale = 1.01
                bpy.ops.transform.resize(value=(scale, scale, scale))
        bpy.context.space_data.pivot_point = 'CENTER'
            
        return {'FINISHED'}
    
class Duckx_OT_UvUnwarpHere(Operator):
    bl_idname = "duckx_tools.uv_unwarp_here_operator"
    bl_label = "UV Unwarp Here"
    bl_icon = "UV"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Rotation UV"

    keepTexel : BoolProperty(name="Keep Texel", default=True)
    
    def execute(self, context):
        bpy.ops.uv.snap_cursor(target='SELECTED')
        
        if self.keepTexel:
            try:
                bpy.ops.object.texel_density_check()
                bpy.ops.object.calculate_to_set()
            except:
                self.report({"INFO"} ,"Request Texel Density")

        bpy.ops.uv.seams_from_islands()        
        bpy.ops.uv.unwrap(fill_holes=False, margin=0)
        bpy.ops.uv.align_rotation()
        
        if self.keepTexel:
            try:
                bpy.ops.object.texel_density_set()
            except:
                self.report({"INFO"} ,"Request Texel Density")
                
        bpy.ops.uv.snap_selected(target='CURSOR_OFFSET')
        return {'FINISHED'}
    
class Duckx_OT_UVPositionRandom(Operator):
    bl_idname = "duckx_tools.uv_position_random_operator"
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


    
def register():
    bpy.utils.register_class(Duckx_OT_ActiveUVMap)
    bpy.utils.register_class(Duckx_OT_UvRotation)
    bpy.utils.register_class(Duckx_OT_UVPadding)
    bpy.utils.register_class(Duckx_OT_UvUnwarpHere)
    bpy.utils.register_class(Duckx_OT_UVPositionRandom)
        
    
def unregister():
    bpy.utils.unregister_class(Duckx_OT_ActiveUVMap)
    bpy.utils.unregister_class(Duckx_OT_UvRotation)
    bpy.utils.unregister_class(Duckx_OT_UVPadding)
    bpy.utils.unregister_class(Duckx_OT_UvUnwarpHere)
    bpy.utils.unregister_class(Duckx_OT_UVPositionRandom)
