import bpy
from bpy.types import (Operator)
from bpy.props import (EnumProperty, PointerProperty, StringProperty, FloatVectorProperty, FloatProperty, IntProperty, BoolProperty)

class Duckx_OT_FlipTools(Operator):
    bl_idname = "duckx_tools.fliptools_operator"
    bl_label = "Flip"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_icon = "MOD_MIRROR"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Flip Object and apply scale"
    
    axis : StringProperty(name="Flip Axis")
    
    def execute(self, context):
        axis = self.axis
        
        
        bpy.ops.view3d.snap_cursor_to_center()
        bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'
        
        
        
        if bpy.context.mode == "EDIT_MESH":
            if axis == "X":
                bpy.ops.transform.resize(value=(-1, 1, 1), orient_type='GLOBAL')
            elif axis == "Y":
                bpy.ops.transform.resize(value=(1, -1, 1), orient_type='GLOBAL')
            elif axis == "Z":
                bpy.ops.transform.resize(value=(1, 1, -1), orient_type='GLOBAL')
            bpy.ops.mesh.flip_normals()
        elif bpy.context.mode == "OBJECT":
            if axis == "X":
                bpy.ops.transform.mirror(orient_type='GLOBAL', constraint_axis=(True, False, False))
            elif axis == "Y":
                bpy.ops.transform.mirror(orient_type='GLOBAL', constraint_axis=(False, True, False))
            elif axis == "Z":
                bpy.ops.transform.mirror(orient_type='GLOBAL', constraint_axis=(False, False, True))
            
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            try:
                bpy.ops.object.editmode_toggle()
            except:
                pass
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.flip_normals()
            try:
                bpy.ops.object.editmode_toggle()
            except:
                pass
            bpy.context.scene.tool_settings.transform_pivot_point = 'BOUNDING_BOX_CENTER'
        
        return {'FINISHED'}
    
def register():
    bpy.utils.register_class(Duckx_OT_FlipTools)
        
    
def unregister():
    bpy.utils.unregister_class(Duckx_OT_FlipTools)
        