import bpy
import bmesh
from bpy.types import (Operator)
from bpy.props import (EnumProperty, PointerProperty, StringProperty, FloatVectorProperty, FloatProperty, IntProperty, BoolProperty)

from . import func_core

class Duckx_OT_ToggleProp(Operator):
    bl_idname = "duckx_tools.toggle_prop_operator"
    bl_label = "Toggle"
    bl_description = "Show/Hide"

    prop_name: bpy.props.StringProperty(name="Property Name") 

    def execute(self, context):
        scene = context.scene
        duckx_tools = scene.duckx_tools
        current_value = getattr(duckx_tools, self.prop_name)
        setattr(duckx_tools, self.prop_name, not current_value)
        print(f"{self.prop_name}: {getattr(duckx_tools, self.prop_name)}")
        
        
        return {'FINISHED'}
    
class Duckx_OT_ConvexTools(Operator):
    bl_idname = "duckx_tools.convex_tools_operator"
    bl_label = "Convex X"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_icon = "MESH_ICOSPHERE"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Make Convex from Object"

    wire : BoolProperty(name="Wire", default=True)
    decimate : FloatProperty(name="Decimate Ratio", min=0, max=1, default=1, step=0.1, precision=4)
    face : FloatProperty(name="Face Ratio", min=0, max=1, default=1, step=0.001, precision=4)
    edge : FloatProperty(name="Edge Ratio", min=0, max=1, default=1, step=0.001, precision=4)  
    
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
        bpy.ops.duckx_tools.merge_by_size_operator(action="face", size = 1 - self.face)
        bpy.ops.mesh.convex_hull()
        bpy.ops.duckx_tools.merge_by_size_operator(action="edge", size = 1 - self.edge)
        bpy.context.object.modifiers["Decimate"].ratio = self.decimate
        bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
        bpy.ops.mesh.convex_hull()
        bpy.context.object.modifiers["Decimate"].use_collapse_triangulate = True
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.convert(target='MESH')
        bpy.context.object.name = "UCX_"+bpy.context.view_layer.active_layer_collection.collection.name
        return {'FINISHED'}

class Duckx_OT_BoxFromMesh(Operator):
    bl_idname = "duckx_tools.box_from_mesh_operator"
    bl_label = "Box From Mesh"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Create Box from Mesh"

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
            bpy.ops.duckx_tools.orienselect_operator()
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
            bpy.ops.duckx_tools.orienglobal_operator()
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
        bpy.ops.duckx_tools.orienselect_operator()
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
    
class Duckx_OT_MoveXTools(Operator):
    bl_idname = "duckx_tools.movex_tools_operator"
    bl_label = "Move X"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_icon = "EMPTY_ARROWS"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Move Between"

    move_axis : EnumProperty(
        name = "Axis",
        items = [('x', "X", ""),('y', "Y", ""), ('z', "Z", "")]
        )
    
    value : FloatProperty(name="Move Value", default=0.1, min=0)
    invert : BoolProperty(name="Invert", default=False)
    any_orient : BoolProperty(name="Any Orient", default=False)
    
    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'
    
    def invoke(self, context, event):
        if event.ctrl:
            self.invert = True
            return self.execute(context)
        else:
            return self.execute(context)
        
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.prop(self, "move_axis", expand=True)
        layout.prop(self, "value")
        layout.prop(self, "invert")
        layout.prop(self, "any_orient")

    
    def execute(self, context):
        if self.any_orient:
            obj = bpy.context.active_object
            bm = bmesh.from_edit_mesh(obj.data)
            if bpy.context.tool_settings.mesh_select_mode[0]:
                selected = len([e for e in bm.verts if e.select])
            elif bpy.context.tool_settings.mesh_select_mode[1]:
                selected = len([e for e in bm.edges if e.select])
            else:
                selected = 0
            pivot = bpy.context.scene.tool_settings.transform_pivot_point
            if selected == 2:
                if self.invert == True:
                    value = self.value*-1
                else:
                    value = self.value
                obj = bpy.context.active_object
                if obj and obj.type == 'MESH' and bpy.context.mode == 'EDIT_MESH':
                    bpy.ops.view3d.snap_cursor_to_active()
                    bpy.ops.mesh.select_prev_item()
                    #bpy.ops.view3d.snap_selected_to_cursor(use_offset=True)
                    bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'
                    
                    if self.move_axis == "x":
                        bpy.ops.transform.resize(value=(0, 1, 1))
                        bpy.ops.transform.translate(value=(value, 0, 0))
                    elif self.move_axis == "y":
                        bpy.ops.transform.resize(value=(1, 0, 1))
                        bpy.ops.transform.translate(value=(0, value, 0))
                    elif self.move_axis == "z":
                        bpy.ops.transform.resize(value=(1, 1, 0))
                        bpy.ops.transform.translate(value=(0, 0, value))
            else:
                print("Please select first and last Edge or Vertex")
                self.report({"INFO"} ,"Please select first and last Edge or Vertex")
                func_core.message_box("Please select first and last Edge or Vertex", "Move Tools", "ERROR")
            bpy.context.scene.tool_settings.transform_pivot_point = pivot
        else:
            oreint = bpy.context.scene.transform_orientation_slots[0].type
            bpy.context.scene.transform_orientation_slots[0].type = 'GLOBAL'
            obj = context.edit_object
            me = obj.data
            bm = bmesh.from_edit_mesh(me)
            bm.edges.ensure_lookup_table()

            cursor_location = bpy.context.scene.cursor.location
            
            edge_list = []
            for element in bm.select_history:
                if isinstance(element, bmesh.types.BMEdge):
                    edge_list.append([element, None])
            
            edge_list.reverse()
            if len(edge_list) >= 1:
                for i in range(len(edge_list)):
                    bpy.ops.mesh.select_all(action='DESELECT')
                    edge_list[i][0].select = True
                    bpy.ops.view3d.snap_cursor_to_selected()
                    
                    edge_list[i][1] = bpy.context.scene.cursor.location.copy()
                    if i > 0:
                        v1 = edge_list[0][0].verts[0]
                        v2 = edge_list[0][0].verts[1]
                        a = (v1.co + v2.co) / 2.0
                        v1 = edge_list[1][0].verts[0]
                        v2 = edge_list[1][0].verts[1]
                        b = (v1.co + v2.co) / 2.0
                        print(a)
                        print(edge_list[0][1])
                        print(edge_list[1][1])
                        co = a - b
                        
                        print(co)
                        if self.move_axis == "x":
                            bpy.ops.transform.translate(value=(co[0], 0, 0))
                            if co[0] < 0:
                                if self.invert:
                                    bpy.ops.transform.translate(value=(-self.value, 0, 0))
                                else:
                                    bpy.ops.transform.translate(value=(self.value, 0, 0))
                            else:
                                if self.invert:
                                    bpy.ops.transform.translate(value=(self.value, 0, 0))
                                else:
                                    bpy.ops.transform.translate(value=(-self.value, 0, 0))
                        elif self.move_axis == "y":
                            bpy.ops.transform.translate(value=(0, co[1], 0))
                            if co[1] < 0:
                                if self.invert:
                                    bpy.ops.transform.translate(value=(0, -self.value, 0))
                                else:
                                    bpy.ops.transform.translate(value=(0, self.value, 0))
                            else:
                                if self.invert:
                                    bpy.ops.transform.translate(value=(0, self.value, 0))
                                else:
                                    bpy.ops.transform.translate(value=(0, -self.value, 0))
                        elif self.move_axis == "z":
                            bpy.ops.transform.translate(value=(0, 0, co[2]))
                            if co[2] < 0:
                                if self.invert:
                                    bpy.ops.transform.translate(value=(0, 0, -self.value))
                                else:
                                    bpy.ops.transform.translate(value=(0, 0, self.value))
                            else:
                                if self.invert:
                                    bpy.ops.transform.translate(value=(0, 0, self.value))
                                else:
                                    bpy.ops.transform.translate(value=(0, 0, -self.value))
            bmesh.update_edit_mesh(me)
            bpy.context.scene.transform_orientation_slots[0].type = oreint
        
        

        return {'FINISHED'}
    
class Duckx_OT_ScaleFromActive(Operator):
    bl_idname = "duckx_tools.scale_from_active_operator"
    bl_label = "Scale From Active"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_icon = "EMPTY_ARROWS"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Scale From Active Selected"

    action : EnumProperty(
        name = "Property",
        items = [('x', "X", ""),('y', "Y", ""), ('z', "Z", "")]
        )
    
    value : FloatProperty(name="Move Value", default=0.1, min=0)
    minus : BoolProperty(name="Minus", default=True)
    
    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'
    
    def execute(self, context):
        pivot = bpy.context.scene.tool_settings.transform_pivot_point
        orient = bpy.context.scene.transform_orientation_slots[0].type

        
        
        bpy.context.scene.tool_settings.transform_pivot_point = 'ACTIVE_ELEMENT'
        bpy.context.scene.transform_orientation_slots[0].type = 'NORMAL'
        bpy.ops.mesh.select_prev_item()
        
        
        bpy.context.scene.transform_orientation_slots[0].type = orient
        bpy.context.scene.tool_settings.transform_pivot_point = pivot

        return {'FINISHED'}

class Duckx_OT_RemoveLoopRing(Operator):
    bl_idname = "duckx_tools.remove_loop_operator"
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
    
class Duckx_OT_RemoveLoopRing(Operator):
    bl_idname = "duckx_tools.remove_loop_ring_operator"
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
    
class Duckx_OT_InvertSeam(Operator):
    bl_idname = "duckx_tools.invert_seam_operator"
    bl_label = "Invert Seam"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_icon = "SHADERFX"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Invert UV seam from edge selected"

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
    
class Duckx_OT_InvertInLooseParts(Operator):
    bl_idname = "duckx_tools.invert_in_loose_parts_operator"
    bl_label = "Invert In Loose Parts"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_icon = "SHADERFX"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Invert selection In Loose Parts"

    def execute(self, context):
        
        obj = context.edit_object
        me = obj.data

        bm = bmesh.from_edit_mesh(me)
        bm.faces.ensure_lookup_table()  # Ensure face data is updated

        faces_a = [] 
        faces_b = []
        for face in bm.faces:
            if face.select:
                faces_a.append(face)
        bpy.ops.mesh.select_all(action='SELECT')
        for face in bm.faces:
            if face.select:
                faces_b.append(face)
        bpy.ops.mesh.select_all(action='DESELECT')
        for face in faces_a:
            face.select = True
        bpy.ops.mesh.select_linked(delimit={'NORMAL'})
        bpy.ops.mesh.hide(unselected=True)
        bpy.ops.mesh.select_all(action='DESELECT')
        for face in faces_a:
            face.select = True
        bpy.ops.mesh.select_all(action='INVERT')
        faces_a.clear()
        for face in bm.faces:
            if face.select:
                faces_a.append(face)
        bpy.ops.mesh.reveal()
        bpy.ops.mesh.select_all(action='DESELECT')
        for face in faces_b:
            face.select = True
        bpy.ops.mesh.hide(unselected=True)
        bpy.ops.mesh.select_all(action='DESELECT')
        for face in faces_a:
            face.select = True
        bmesh.update_edit_mesh(me)
        return {'FINISHED'}
    
class Duckx_OT_MoveVertexToActive(Operator):
    bl_idname = "duckx_tools.move_vert_to_active_operator"
    bl_label = "Move Vertex To Active"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_icon = "ARROW_LEFTRIGHT"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Multiple Couple Merge Vertex"

    def execute(self, context):
        # obj = bpy.context.active_object
            
        # vertex_list = func_core.selected_vertexs(obj)
        # a_vert_index, a_vert_co = func_core.active_vertex()
        # print(a_vert_index)
        # print(a_vert_co)
        # bpy.ops.mesh.select_prev_item()
        # b_vert_index, b_vert_co = func_core.active_vertex()
        # print(b_vert_index)
        # print(b_vert_co)
        # if a_vert_co and b_vert_co != None:
        #     local = a_vert_co - b_vert_co
        #     print(f"New location: {local}")
        #     bpy.ops.transform.translate(value=(local), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL')

        # bpy.ops.mesh.select_all(action='DESELECT')
        # func_core.select_vertexs(obj, vertex_list)
        # bpy.ops.duckx_tools.utilities_operator(action="Scale 0")
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

class Duckx_OT_SelectByDistance(Operator):
    bl_idname = "duckx_tools.select_by_distance_operator"
    bl_label = "Select By Distance"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_icon = "FIXED_SIZE"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Select By Distance and Next"

    distance : FloatProperty(name="Distance", precision=5)
    threshold : FloatProperty(name="Threshold", default=0.000, precision=5, step=0.0010)
    
    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        obj = context.edit_object
        me = obj.data

        bm = bmesh.from_edit_mesh(me)
        bm.faces.ensure_lookup_table()  # Ensure face data is updated

        if bpy.context.tool_settings.mesh_select_mode[2]:
            face_list = []
            for face in bm.faces:
                if face.select:
                    face_list.append(face)
            if len(face_list) > 1:
                a = face_list[0].calc_center_median().length
                print(a)
                b = face_list[-1].calc_center_median().length
                print(b)
                self.distance = round(a - b, 5)
                print(abs(round(a - b, 5)))
                # for face in bm.faces:
                #     new_distance = round(b - face.calc_center_median().length, 5)
                #     # print(new_distance, round(self.distance - self.threshold, 5))
                #     print(new_distance, round(self.distance, 5))
                #     if new_distance >= round(self.distance, 5):
                #         print(new_distance)
                # #         face.select = True
                # # b = face.calc_center_median().length

        bmesh.update_edit_mesh(me)
        return {'FINISHED'}

class Duckx_OT_Utilities(Operator):
    bl_idname = "duckx_tools.utilities_operator"
    bl_label = "Utilities Tools"
    bl_description = "Utilities Tools"

    action : StringProperty(name="Action")

    def execute(self, context):
        action = self.action
        scene = context.scene
        duckx_tools = scene.duckx_tools
        
        if action == "Scale 0":
            pivot = bpy.context.scene.tool_settings.transform_pivot_point
            orient = bpy.context.scene.transform_orientation_slots[0].type
            if not context.area.type == 'IMAGE_EDITOR':
                bpy.context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'
                bpy.context.scene.tool_settings.use_transform_correct_face_attributes = True
                bpy.ops.transform.resize(value=(0, 0, 0), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, proportional_edit_falloff='RANDOM', proportional_size=0.122846, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'FACE'}, use_snap_project=False, snap_target='CENTER', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
                bpy.ops.mesh.merge(type='CENTER')
                bpy.context.scene.tool_settings.transform_pivot_point = 'BOUNDING_BOX_CENTER'
            else:
                bpy.ops.transform.resize(value=(0, 0, 0), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, proportional_edit_falloff='RANDOM', proportional_size=0.122846, use_proportional_connected=False, use_proportional_projected=False, snap=False, snap_elements={'FACE'}, use_snap_project=False, snap_target='CENTER', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)
                bpy.ops.uv.weld()
            bpy.context.scene.tool_settings.transform_pivot_point = pivot
            bpy.context.scene.transform_orientation_slots[0].type = orient
        
        elif action == "Origin to selection":
            bpy.ops.view3d.snap_cursor_to_selected()
            bpy.ops.object.editmode_toggle()
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
        
        elif action == "Boundary Sharp":
            bpy.ops.mesh.region_to_loop()
            bpy.ops.mesh.mark_sharp()
            
        elif action == "Deparate":
            bpy.ops.mesh.duplicate_move(MESH_OT_duplicate={"mode":1}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_type":'GLOBAL', "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'RANDOM', "proportional_size":0.179859, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_elements":{'VERTEX'}, "use_snap_project":False, "snap_target":'CLOSEST', "use_snap_self":True, "use_snap_edit":True, "use_snap_nonedit":True, "use_snap_selectable":False, "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "view2d_edge_pan":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})
            bpy.ops.mesh.separate(type='SELECTED')
            bpy.ops.object.editmode_toggle()
            obj = context.object
            func_core.deselect_objects_by_name(obj.name)
            selected_objects = bpy.context.selected_objects
            for obj in selected_objects:
                bpy.context.view_layer.objects.active = obj

        elif action == "Correct Face Att":
            if bpy.context.scene.tool_settings.use_transform_correct_face_attributes == True:
                bpy.context.scene.tool_settings.use_transform_correct_face_attributes = False
            else:
                bpy.context.scene.tool_settings.use_transform_correct_face_attributes = True

        elif action == "Delete Loose Part":
            bpy.ops.mesh.select_linked(delimit={'NORMAL'})
            bpy.ops.mesh.select_more()
            bpy.ops.mesh.select_linked(delimit={'NORMAL'})
            bpy.ops.mesh.select_more()
            bpy.ops.mesh.select_linked(delimit={'NORMAL'})
            bpy.ops.mesh.select_more()
            bpy.ops.mesh.delete(type='FACE')
        
        elif action == "Edge Length":
            #self.report({"ERROR"} , str(func_core.EdgeLength()))
            func_core.clipboard(func_core.edge_length())
            func_core.message_box(str(round(func_core.edge_length(), 3)), "Edge Length", "CON_DISTLIMIT")
            
            #func_core.move_selected_uv(1,1)
            func_core.move_selected_uv_island(0,0)

        return {'FINISHED'}
    
class Duckx_OT_ConsoleCommand(Operator):
    bl_idname = "duckx_tools.console_command_operator"
    bl_label = "Console Command"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_icon = "CONSOLE"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Type Command"
    
    cc : StringProperty(name="Command")
    def execute(self, context):
        cc = self.cc
        
        if cc == "test":
            view = bpy.context.scene.view_layers['View Layer']
            stats = bpy.context.scene.statistics(view) #returns string
            print(stats)

        else:
            self.report({"INFO"} ,"Wrong Command")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        
        wm = context.window_manager
        return wm.invoke_props_dialog(self)


    
classes = [Duckx_OT_ToggleProp, Duckx_OT_ConvexTools, Duckx_OT_BoxFromMesh, Duckx_OT_MeshToBox,
           Duckx_OT_MoveXTools, Duckx_OT_ScaleFromActive, Duckx_OT_RemoveLoopRing, Duckx_OT_InvertSeam,
           Duckx_OT_InvertInLooseParts, Duckx_OT_SelectByDistance,
           Duckx_OT_MoveVertexToActive, Duckx_OT_Utilities, Duckx_OT_ConsoleCommand]
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
           
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)