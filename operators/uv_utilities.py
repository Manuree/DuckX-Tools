import bpy
from bpy.types import (Context, Event, Operator)
from bpy.props import (EnumProperty, PointerProperty, StringProperty, FloatVectorProperty, FloatProperty, IntProperty, BoolProperty)

from . import func_core
import math

class Duckx_OT_ActiveUVMap(Operator):
    bl_idname = "duckx_tools.active_uv_map_operator"
    bl_label = "UV Map"
    bl_description = "UV Maps Tools"

    action : StringProperty(name="Action")
    
    @classmethod
    def poll(cls, context):
        selected_object = context.active_object
        return context.selected_objects and selected_object.type == 'MESH'
    
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
    bl_description = "Rotation UV / Hold Shift for rotate from selected face"

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


    
def register():
    bpy.utils.register_class(Duckx_OT_ActiveUVMap)
    bpy.utils.register_class(Duckx_OT_UvRotation)
    bpy.utils.register_class(Duckx_OT_UVPadding)
    bpy.utils.register_class(Duckx_OT_UvUnwarpHere)
        
    
def unregister():
    bpy.utils.unregister_class(Duckx_OT_ActiveUVMap)
    bpy.utils.unregister_class(Duckx_OT_UvRotation)
    bpy.utils.unregister_class(Duckx_OT_UVPadding)
    bpy.utils.unregister_class(Duckx_OT_UvUnwarpHere)
