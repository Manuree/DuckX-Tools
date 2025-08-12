import bpy
import bmesh
from bpy.types import (Operator)
from bpy.props import (EnumProperty, PointerProperty, StringProperty, FloatVectorProperty, FloatProperty, IntProperty, BoolProperty)

from ..icon_reg import *
from . import func_core
from ..ui import add_panel, add_expand_panel



class Duckx_OT_ConvexTools(Operator):
    bl_idname = "duckx_tools.convex_tools"
    bl_label = "Convex X"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_icon = "MESH_ICOSPHERE"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Make Convex from Object"

    wire : BoolProperty(name="Wire", default=True)
    decimate : FloatProperty(name="Decimate Ratio", min=0, max=1, default=0.15, step=0.1, precision=4)
    face : FloatProperty(name="Face Ratio", min=0, max=1, default=1, step=0.001, precision=4)
    edge : FloatProperty(name="Edge Ratio", min=0, max=1, default=1, step=0.001, precision=4)  
    
    @classmethod
    def poll(cls, context):
        return (
            context.object.type == 'MESH' and
            context.active_object is not None and
            len(context.selected_objects) > 0
        )


    def execute(self, context):
        if self.wire:
            bpy.context.object.show_wire = True
        else:
            bpy.context.object.show_wire = False
        
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.convex_hull()
        bpy.ops.object.modifier_add(type='DECIMATE')
        bpy.ops.mesh.convex_hull()
        bpy.ops.duckx_tools.merge_by_size(action="face", size = 1 - self.face)
        bpy.ops.mesh.convex_hull()
        bpy.ops.duckx_tools.merge_by_size(action="edge", size = 1 - self.edge)
        bpy.context.object.modifiers["Decimate"].ratio = self.decimate
        bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
        bpy.ops.mesh.convex_hull()
        bpy.context.object.modifiers["Decimate"].use_collapse_triangulate = True
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.convert(target='MESH')
        bpy.context.object.name = "UCX_"+bpy.context.view_layer.active_layer_collection.collection.name
        return {'FINISHED'}

class Duckx_OT_BoxFromMesh(Operator):
    bl_idname = "duckx_tools.box_from_mesh"
    bl_label = "Box From Mesh"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Create Box from Mesh"

    @classmethod
    def poll(cls, context):
        return (
            context.object.type == 'MESH' and
            context.active_object is not None and
            len(context.selected_objects) > 0
        )


    def execute(self, context):
        obj = bpy.context.active_object
        if obj and obj.type == 'MESH' and bpy.context.mode == 'EDIT_MESH':
            name = bpy.context.object.name
            bpy.ops.mesh.duplicate_move(MESH_OT_duplicate={"mode":1})
            bpy.ops.mesh.separate(type='SELECTED')
            bpy.ops.object.mode_set(mode='OBJECT')
            func_core.deselect_object_by_name(name)
            obj = bpy.context.selected_objects
            bpy.context.view_layer.objects.active = obj[0]
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.separate(type='LOOSE')
            bpy.ops.object.mode_set(mode='OBJECT')
        elif obj and obj.type == 'MESH' and bpy.context.mode == 'OBJECT':
            bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'})

        objs = func_core.objects_to_list()
        for obj in objs:
            func_core.select_object_by_name(obj)
            func_core.select_face_by_size("L")
            bpy.ops.duckx_tools.orienfromselect()
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
            #bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='BOUNDS')
            bpy.context.scene.tool_settings.use_transform_data_origin = True
            bpy.ops.transform.transform(mode='ALIGN', orient_type="Face")
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
            bpy.context.scene.tool_settings.use_transform_data_origin = False

            bpy.ops.view3d.snap_cursor_to_selected()
            selectObject = bpy.context
            selectObject.object
            lo : FloatVectorProperty(name="Object Location")
            ro : FloatVectorProperty(name="Object Rotation")
            di : FloatVectorProperty(name="Object Dimensions")
            lo = selectObject.object.location
            ro = selectObject.object.rotation_euler
            di = selectObject.object.dimensions
            bpy.ops.mesh.primitive_cube_add()
            selectObject = bpy.context
            selectObject.object
            bpy.context.object.location = lo
            bpy.context.object.rotation_euler = ro
            bpy.context.object.dimensions = di
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            bpy.context.object.name = "UBX_"+bpy.context.view_layer.active_layer_collection.collection.name
            bpy.ops.object.select_all(action='DESELECT')
            func_core.select_object_by_name(obj)
            bpy.ops.object.delete(use_global=False)
            bpy.ops.duckx_tools.orienglobal()
        return {'FINISHED'}
    
class Duckx_OT_MeshToBox(Operator):
    bl_idname = "duckx_tools.mesh_to_box_operator"
    bl_label = "Mesh to Box"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Convert Mesh To Box"

    box_offset : FloatProperty(name="Box Offset", min=0, max=1, default=0.0001, step=0.0001, precision=4)
    remove_doubles : FloatProperty(name="Remove Doubles", min=0, max=1, default=0.0002, step=0.0001, precision=4)
    fill_hole : BoolProperty(name="Fill Hole", default=True)

    @classmethod
    def poll(cls, context):
        return (
            context.mode == 'EDIT_MESH' and
            context.active_object is not None and
            len(context.selected_objects) > 0
        )

    
    def execute(self, context):
        pivot = bpy.context.scene.tool_settings.transform_pivot_point
        orient = bpy.context.scene.transform_orientation_slots[0].type
        
        
        

        obj = bpy.context.active_object
        main_object = obj
        print(f"Main Object {main_object.name}")
        bpy.ops.mesh.separate(type='SELECTED')
        func_core.deselect_object_by_name(main_object.name)
        obj = bpy.context.selected_objects
        func_core.select_object_by_name(obj[0].name)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.object.mode_set(mode='OBJECT')
        sub_object = bpy.context.active_object
        print(f"Sub Object {sub_object.name}")

        #Create Box
        func_core.select_face_by_size("L")
        bpy.ops.duckx_tools.orienfromselect()
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        bpy.context.scene.tool_settings.use_transform_data_origin = True
        bpy.ops.transform.transform(mode='ALIGN', orient_type="Face")
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        bpy.context.scene.tool_settings.use_transform_data_origin = False
        bpy.ops.view3d.snap_cursor_to_selected()
        selectObject = bpy.context
        selectObject.object
        lo : FloatVectorProperty(name="Object Location")
        ro : FloatVectorProperty(name="Object Rotation")
        di : FloatVectorProperty(name="Object Dimensions")
        lo = selectObject.object.location
        ro = selectObject.object.rotation_euler
        di = selectObject.object.dimensions
        bpy.ops.mesh.primitive_cube_add()
        selectObject = bpy.context
        selectObject.object
        bpy.context.object.location = lo
        bpy.context.object.rotation_euler = ro
        bpy.context.object.dimensions = di
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.context.object.name = "UBX_"+bpy.context.view_layer.active_layer_collection.collection.name
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.transform.shrink_fatten(value=self.box_offset, use_even_offset=True, mirror=True)
        bpy.ops.object.mode_set(mode='OBJECT')
        box = bpy.context.active_object
        print(f"Box Object {box.name}")


        #Add Boolean
        bpy.ops.object.select_all(action='DESELECT')
        func_core.select_object_by_name(sub_object.name)
        bpy.ops.object.modifier_add(type='BOOLEAN')
        bpy.context.object.modifiers["Boolean"].object = box
        bpy.context.object.modifiers["Boolean"].operation = 'INTERSECT'
        if self.fill_hole:
            bpy.context.object.modifiers["Boolean"].use_self = True




        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.edge_split(type='EDGE')
        bpy.context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'
        bpy.context.scene.transform_orientation_slots[0].type = 'NORMAL'
        bpy.context.scene.tool_settings.use_transform_correct_face_attributes = True
        bpy.ops.transform.resize(value=(20, 20,20))
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.convert(target='MESH')
        bpy.ops.object.select_all(action='DESELECT')
        func_core.select_object_by_name(box.name)
        bpy.ops.object.delete(use_global=False)
        func_core.select_object_by_name(sub_object.name)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles(threshold=self.remove_doubles)
        bpy.ops.object.mode_set(mode='OBJECT')
        func_core.select_object_by_name(main_object.name)
        bpy.ops.object.join()
        bpy.ops.object.mode_set(mode='EDIT')
        
        bpy.context.scene.tool_settings.transform_pivot_point = pivot
        bpy.context.scene.transform_orientation_slots[0].type = orient

        return {'FINISHED'}
    

def draw_shape_tools(self, context, layout, props):
    row = layout.row(align=True)
    row.scale_y = 1.5
    row.scale_x = 5
    row.operator("duckx_tools.convex_tools", text="", icon=bl_icons("MESH_ICOSPHERE"))
    row.operator("duckx_tools.box_from_mesh", text="", icon=bl_icons("MESH_CUBE"))
    row.operator("duckx_tools.mesh_to_box_operator", text="Mesh to box")
    return layout



add_expand_panel("Shape", draw_shape_tools)



classes = [Duckx_OT_ConvexTools, Duckx_OT_BoxFromMesh, Duckx_OT_MeshToBox]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
           
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)