import bpy
import bmesh
from bpy.types import (Operator)
from bpy.props import (EnumProperty, PointerProperty, StringProperty, FloatVectorProperty, FloatProperty, IntProperty, BoolProperty)

from ..icon_reg import *
from . import func_core
from ..ui import add_panel, add_expand_panel

class Duckx_OT_AddEmpty(Operator):
    bl_idname = "duckx_tools.add_empty"
    bl_label = "Add Empty"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_description = "Add an Empty Object"
    bl_options = {"REGISTER", "UNDO"}

    prefix : StringProperty(name="Prefix", default="COM_")
    name_type : EnumProperty(
        name="Type",
        items=[
            ('COLLECTION', "Collection", ""),
            ('OBJECT', "Object", "")
        ]
    )

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text="Name from:")
        row = col.row(align=True)
        row.prop(self, "name_type", expand=True)
        col = layout.column()
        col.prop(self, "prefix")

    def execute(self, context):
        name = ""
        if self.name_type == 'COLLECTION':
            # get the active collection name
            active_collection = context.view_layer.active_layer_collection
            if active_collection:
                name = active_collection.name
        else:
            # get the active object name
            active_object = context.active_object
            if active_object:
                name = active_object.name

        if context.mode == 'EDIT_MESH':
            bpy.ops.view3d.snap_cursor_to_selected()
            bpy.ops.duckx_tools.orienfromselect()
            bpy.ops.object.mode_set(mode='OBJECT')
        else:       
            bpy.ops.view3d.snap_cursor_to_selected()
            bpy.ops.duckx_tools.orienglobal()

        bpy.ops.object.empty_add(type='ARROWS')
        empty = context.active_object
        empty.name = self.prefix + name
        bpy.ops.transform.transform(mode='ALIGN')

        return {'FINISHED'}
    
class Duckx_OT_ScaleZero(Operator):
    bl_idname = "duckx_tools.scale_zero"
    bl_label = "Scale to Zero"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_description = "Scale selected to zero"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object is not None and 
                context.object.type == 'MESH' and 
                context.mode == 'EDIT_MESH')
    
    def execute(self, context):
        pivot = bpy.context.scene.tool_settings.transform_pivot_point
        orient = bpy.context.scene.transform_orientation_slots[0].type
        if not context.area.type == 'IMAGE_EDITOR':
            bpy.context.scene.tool_settings.transform_pivot_point = 'BOUNDING_BOX_CENTER'
            bpy.context.scene.tool_settings.use_transform_correct_face_attributes = True
            bpy.ops.transform.resize(value=(0, 0, 0))
            bpy.ops.mesh.merge(type='CENTER')
        else:
            bpy.ops.transform.resize(value=(0, 0, 0))
            bpy.ops.uv.weld()
        bpy.context.scene.tool_settings.transform_pivot_point = pivot
        bpy.context.scene.transform_orientation_slots[0].type = orient
        return {'FINISHED'}
        
class Duckx_OT_CoupleMergeVertex(Operator):
    bl_idname = "duckx_tools.couple_merge_vertex"
    bl_label = "Couple Merge Vertex"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_icon = "ARROW_LEFTRIGHT"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Multiple Couple Merge Vertex \nPlease Select Vertex > 21"

    @classmethod
    def poll(cls, context):
        return (context.object is not None and 
                context.object.type == 'MESH' and 
                context.mode == 'EDIT_MESH' and
                context.tool_settings.mesh_select_mode[0] and
                context.object.data.total_vert_sel > 1)

    def execute(self, context):
        obj = bpy.context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        vertex_list = []
        for element in bm.select_history:
            if isinstance(element, bmesh.types.BMVert):
                vertex_list.append(element)
        print(vertex_list)
        bpy.ops.mesh.select_all(action='DESELECT')
        for i in range(len(vertex_list)):
            if i % 2 == 0:
                print(f"Index: {vertex_list[i]}")
                vertex_list[i].select = True
            else:
                new_loc = vertex_list[i].co - vertex_list[i-1].co
                print(f"To Index: {new_loc}")
                orient = bpy.context.scene.transform_orientation_slots[0].type 
                bpy.context.scene.transform_orientation_slots[0].type = 'LOCAL'
                bpy.ops.transform.translate(value=(new_loc), orient_type='LOCAL')
                bpy.ops.mesh.select_all(action='DESELECT')
                bpy.context.scene.transform_orientation_slots[0].type = orient
        for vertex in vertex_list:
            vertex.select = True
        bpy.ops.mesh.remove_doubles()
        bmesh.update_edit_mesh(me)
        return {'FINISHED'}

class Duckx_OT_DuplicateAndSeparate(Operator):
    bl_idname = "duckx_tools.duplicate_and_separate"
    bl_label = "Duplicate and Separate"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_icon = "UV_DATA"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Manage UV Maps \nPlease Select Vertex, Edge or Face"

    @classmethod
    def poll(cls, context):
        return (context.object is not None and 
                context.object.type == 'MESH' and 
                context.mode == 'EDIT_MESH' and
                (context.object.data.total_vert_sel > 0 or 
                 context.object.data.total_edge_sel > 0 or 
                 context.object.data.total_face_sel > 0))    

    def execute(self, context):
        bpy.ops.mesh.duplicate_move(MESH_OT_duplicate={"mode":1}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_type":'GLOBAL', "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'RANDOM', "proportional_size":0.179859, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_elements":{'VERTEX'}, "use_snap_project":False, "snap_target":'CLOSEST', "use_snap_self":True, "use_snap_edit":True, "use_snap_nonedit":True, "use_snap_selectable":False, "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "view2d_edge_pan":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})
        bpy.ops.mesh.separate(type='SELECTED')
        bpy.ops.object.editmode_toggle()
        obj = context.object
        func_core.deselect_objects_by_name(obj.name)
        selected_objects = bpy.context.selected_objects
        for obj in selected_objects:
            bpy.context.view_layer.objects.active = obj
        return {'FINISHED'}

class Duckx_OT_OriginFromSelection(Operator):
    bl_idname = "duckx_tools.origin_from_selection"
    bl_label = "Origin from Selection"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_icon = "ORIGIN"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Set Object Origin to Selection"

    @classmethod
    def poll(cls, context):
        return (context.object is not None and 
                context.object.type == 'MESH' and 
                context.mode == 'EDIT_MESH')

    def execute(self, context):
        bpy.ops.view3d.snap_cursor_to_selected()
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
        return {'FINISHED'}


class Duckx_OT_BoundaryTools(Operator):
    bl_idname = "duckx_tools.boundary_tools"
    bl_label = "Boundary Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_icon = "BORDER_RECT"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Select Boundary Vertices - Press 1: Select, 2: Mark Sharp, 3: Clear Sharp, ESC: Cancel"

    @classmethod
    def poll(cls, context):
        return (context.object is not None and 
                context.object.type == 'MESH' and 
                context.mode == 'EDIT_MESH')

    action : EnumProperty(name="Action",
                          items=[
            ('SELECT', "Select", "Select Boundary Vertices"),
            ('MARK_SHARP', "Mark Sharp", "Mark Boundary Vertices as Sharp"),
            ('CLEAR_SHARP', "Clear Sharp", "Clear Sharp Mark from Boundary Vertices")
        ],
        default='SELECT'
    )

    def modal(self, context, event):
        # แสดงข้อความใน header
        context.area.header_text_set("Boundary Tools - Press [1]: Select, [2]: Mark Sharp, [3]: Clear Sharp, ESC: Cancel")
        
        if event.type in {'LEFTMOUSE', 'RIGHTMOUSE', 'ESC'}:
            # ยกเลิกการทำงาน
            context.area.header_text_set(None)
            return {'CANCELLED'}
        
        elif event.type == 'ONE' and event.value == 'PRESS':
            # กด 1 - Select Boundary
            self.action = 'SELECT'
            self.execute_action(context)
            context.area.header_text_set(None)
            return {'FINISHED'}
            
        elif event.type == 'TWO' and event.value == 'PRESS':
            # กด 2 - Mark Sharp
            self.action = 'MARK_SHARP'
            self.execute_action(context)
            context.area.header_text_set(None)
            return {'FINISHED'}
            
        elif event.type == 'THREE' and event.value == 'PRESS':
            # กด 3 - Clear Sharp
            self.action = 'CLEAR_SHARP'
            self.execute_action(context)
            context.area.header_text_set(None)
            return {'FINISHED'}
        
        # ส่งต่อ event อื่นๆ
        return {'PASS_THROUGH'}

    def execute_action(self, context):
        """ทำการ execute action ที่เลือก"""
        if context.object and context.object.type == 'MESH':
            if context.mode == 'EDIT_MESH':
                if self.action == 'SELECT':
                    bpy.ops.mesh.region_to_loop()
                    self.report({'INFO'}, "Boundary vertices selected")
                elif self.action == 'MARK_SHARP':
                    bpy.ops.mesh.region_to_loop()
                    bpy.ops.mesh.mark_sharp()
                    self.report({'INFO'}, "Boundary edges marked sharp")
                elif self.action == 'CLEAR_SHARP':
                    bpy.ops.mesh.region_to_loop()
                    bpy.ops.mesh.mark_sharp(clear=True)
                    self.report({'INFO'}, "Sharp marks cleared from boundary edges")
            else:
                self.report({'WARNING'}, "Must be in Edit Mode")
        else:
            self.report({'WARNING'}, "No mesh object selected")

    def invoke(self, context, event):
        # เริ่ม modal mode
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        # ถ้าเรียกจาก UI หรือ command line
        self.execute_action(context)
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.prop(self, "action", expand=True)

    
class Duckx_OT_InvertInLooseParts(Operator):
    bl_idname = "duckx_tools.invert_in_loose_parts"
    bl_label = "Invert In Loose Parts"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_icon = "SHADERFX"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Invert selection In Loose Parts"

    @classmethod
    def poll(cls, context):
        return (context.object is not None and 
                context.object.type == 'MESH' and 
                context.mode == 'EDIT_MESH')

    def execute(self, context):
        obj = context.edit_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        
        # Ensure all lookup tables are updated
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        # Get current selection mode
        select_mode = context.tool_settings.mesh_select_mode[:]
        
        # Store original selection based on selection mode
        original_selection = []
        all_elements = []
        
        if select_mode[0]:  # Vertex mode
            for vert in bm.verts:
                if vert.select:
                    original_selection.append(vert)
            all_elements = list(bm.verts)
        elif select_mode[1]:  # Edge mode
            for edge in bm.edges:
                if edge.select:
                    original_selection.append(edge)
            all_elements = list(bm.edges)
        elif select_mode[2]:  # Face mode
            for face in bm.faces:
                if face.select:
                    original_selection.append(face)
            all_elements = list(bm.faces)

        # Store all elements for later comparison
        bpy.ops.mesh.select_all(action='SELECT')
        all_selected_elements = []
        
        if select_mode[0]:  # Vertex mode
            for vert in bm.verts:
                if vert.select:
                    all_selected_elements.append(vert)
        elif select_mode[1]:  # Edge mode
            for edge in bm.edges:
                if edge.select:
                    all_selected_elements.append(edge)
        elif select_mode[2]:  # Face mode
            for face in bm.faces:
                if face.select:
                    all_selected_elements.append(face)

        # Deselect all and restore original selection
        bpy.ops.mesh.select_all(action='DESELECT')
        for element in original_selection:
            element.select = True

        # Select linked elements (this works for all selection modes)
        bpy.ops.mesh.select_linked(delimit={'NORMAL'})
        
        # Hide unselected elements
        bpy.ops.mesh.hide(unselected=True)
        
        # Deselect all and restore original selection
        bpy.ops.mesh.select_all(action='DESELECT')
        for element in original_selection:
            if not element.hide:  # Only select if not hidden
                element.select = True

        # Invert selection within visible elements
        bpy.ops.mesh.select_all(action='INVERT')
        
        # Store inverted selection
        inverted_selection = []
        if select_mode[0]:  # Vertex mode
            for vert in bm.verts:
                if vert.select and not vert.hide:
                    inverted_selection.append(vert)
        elif select_mode[1]:  # Edge mode
            for edge in bm.edges:
                if edge.select and not edge.hide:
                    inverted_selection.append(edge)
        elif select_mode[2]:  # Face mode
            for face in bm.faces:
                if face.select and not face.hide:
                    inverted_selection.append(face)

        # Reveal all elements
        bpy.ops.mesh.reveal()
        
        # Select all elements
        bpy.ops.mesh.select_all(action='SELECT')
        for element in all_selected_elements:
            element.select = True
            
        # Hide unselected (show only the loose parts we want to work with)
        bpy.ops.mesh.hide(unselected=True)
        
        # Deselect all and apply inverted selection
        bpy.ops.mesh.select_all(action='DESELECT')
        for element in inverted_selection:
            if not element.hide:  # Only select if not hidden
                element.select = True

        # Update the mesh
        bmesh.update_edit_mesh(me)
        
        return {'FINISHED'}
    
class Duckx_OT_RemoveLoopRing(Operator):
    bl_idname = "duckx_tools.remove_loop_ring"
    bl_label = "Remove Loop Ring"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_icon = "EMPTY_ARROWS"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Select geometry that has similar certain properties to the ones selected"

    action : EnumProperty(
        name = "Property",
        items = [("loop", "Loop", ""),
                 ("ring", "Ring", ""),
                 ("loop_ring", "Loop Ring", "")
                 ]
    )
    loop : IntProperty(name="Loop", default=100, min=0)
    delete : BoolProperty(name="Delete", default=False)
    def execute(self, context):
        for i in range(self.loop): 
            bpy.ops.mesh.select_next_item()
        
        if self.action == "loop":
            bpy.ops.mesh.loop_multi_select(ring=False)
        elif self.action == "ring":
            bpy.ops.mesh.loop_multi_select(ring=True)
        elif self.action == "loop_ring":
            bpy.ops.mesh.loop_multi_select(ring=False)
            bpy.ops.mesh.loop_multi_select(ring=True)
        
        mode = bpy.context.tool_settings.mesh_select_mode[:]
        #print(bpy.context.tool_settings.mesh_select_mode[:])
        # obj = bpy.context.active_object
        if self.delete:
            if mode[0]:
                bpy.ops.mesh.dissolve_verts()
            elif mode[1]:
                bpy.ops.mesh.dissolve_edges()
            elif mode[2]:
                bpy.ops.mesh.dissolve_faces()
        
        return {'FINISHED'}

class Duckx_OT_CorrectFace(Operator):
    bl_idname = "duckx_tools.correct_face_attributes"
    bl_label = "Correct face attributes"

    def execute(self, context):
        if bpy.context.scene.tool_settings.use_transform_correct_face_attributes == True:
            bpy.context.scene.tool_settings.use_transform_correct_face_attributes = False
        else:
            bpy.context.scene.tool_settings.use_transform_correct_face_attributes = True
        return {'FINISHED'}
    
class Duckx_OT_DeleteLooseParts(Operator):
    bl_idname = "duckx_tools.delete_loose_parts"
    bl_label = "Utilities Tools"
    bl_description = "Utilities Tools"


    def execute(self, context):
        bpy.ops.mesh.select_linked(delimit={'NORMAL'})
        bpy.ops.mesh.select_more()
        bpy.ops.mesh.select_linked(delimit={'NORMAL'})
        bpy.ops.mesh.select_more()
        bpy.ops.mesh.select_linked(delimit={'NORMAL'})
        bpy.ops.mesh.select_more()
        bpy.ops.mesh.delete(type='FACE')
        return {'FINISHED'}
    

            

class Duckx_OT_ConsoleCommand(Operator):
    bl_idname = "duckx_tools.console_command"
    bl_label = "Console Command"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_icon = "CONSOLE"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Type Command"
    
    cc : StringProperty(name="Command")
    def execute(self, context):
        cc = self.cc
        scene = context.scene
        duckx_tools = scene.duckx_tools
        
        if cc == "test":
            pass

        else:
            self.report({"INFO"} ,"Wrong Command")
            
            


        return {'FINISHED'}
    
    def invoke(self, context, event):
        
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

def draw_panel_empty(self, context, layout, props):
    row = layout.row(align=True)
    row.operator("duckx_tools.add_empty", text="Add Empty", icon=bl_icons("EMPTY_ARROWS"))
    return row

def draw_panel_scale_zero(self, context, layout, props):
    row = layout.row(align=True)
    col = row.column(align=True)
    col.operator("duckx_tools.scale_zero", text="Scale 0", icon=bl_icons("DOT"))
    col.operator("duckx_tools.couple_merge_vertex", text="Couple Merge Vertex")
    col = row.column(align=True)
    col.operator("duckx_tools.duplicate_and_separate", text="Dup & Sep", icon=bl_icons("DUPLICATE"))
    col.operator("duckx_tools.origin_from_selection", text="Origin From Select")
    return layout

def draw_panel_boundary_tools(self, context, layout, props):
    row = layout.row(align=True)
    col = row.column(align=True)
    col.operator("duckx_tools.boundary_tools", text="Boundary Tools", icon=bl_icons("MESH_PLANE")).action = 'SELECT'
    col.operator("duckx_tools.invert_in_loose_parts", text="Invert In Loose Parts", icon=bl_icons("MOD_EXPLODE"))
    return layout


def draw_expand_panel(layself, context, layout, propsout):
    row = layout.row(align=True)
    row.operator("duckx_tools.console_command", text="Run Command", icon="CONSOLE")
    return row
    
add_panel("Add_Empty", draw_panel_empty)
add_panel("Scale_Zero", draw_panel_scale_zero)
add_panel("Boundary_Tools", draw_panel_boundary_tools)
add_expand_panel("Console", draw_expand_panel)

classes = [Duckx_OT_AddEmpty, Duckx_OT_ScaleZero, Duckx_OT_CoupleMergeVertex, Duckx_OT_DuplicateAndSeparate, 
           Duckx_OT_OriginFromSelection, Duckx_OT_BoundaryTools, Duckx_OT_InvertInLooseParts,
           Duckx_OT_RemoveLoopRing, Duckx_OT_CorrectFace, Duckx_OT_DeleteLooseParts,
           Duckx_OT_ConsoleCommand]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
           
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)