import bpy


from . import icon_reg
from . import properties
from . import setting
from .operators import func_core
from .operators import group_tools
from .operators import triangles_tools


from bpy.types import Panel
from bpy.types import Menu
from bpy.types import Scene
from bpy.types import Header



class VIEW3D_PT_Duckx_MainPanel(Panel):
    bl_idname = "VIEW3D_PT_Duckx_Main_panel"
    bl_label = " Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "🦆"
    #bl_width = 1000

    def draw_header(self, context):

        layout = self.layout
        row = layout.row(align=True)
        row.scale_x = 0.885
        row.label(text="", icon_value=icon_reg.iconLib("logo_D"))
        row.label(text="", icon_value=icon_reg.iconLib("logo_U"))
        row.label(text="", icon_value=icon_reg.iconLib("logo_C"))
        row.label(text="", icon_value=icon_reg.iconLib("logo_K"))
        row.label(text="", icon_value=icon_reg.iconLib("logo_X"))
        #layout.label(text="Tools")
        

    def draw(self, context):
        scene = context.scene
        duckx_tools = scene.duckx_tools        
        selected_objects = context.selected_objects
        active_object = context.active_object

        layout = self.layout
        
        #Object Info
        if duckx_tools.object_name or duckx_tools.mesh_name or duckx_tools.uvmaps or duckx_tools.custom_props :
            if active_object:
                if active_object.type == 'MESH':
                    box = layout.box()
                    col = box.column()
                    row = col.row()
                    if duckx_tools.object_name == True:
                        row.label(text="", icon="OUTLINER_OB_MESH")
                        row.prop(active_object, "name", text="")
                        row = col.row()

                    if duckx_tools.mesh_name == True:
                        row.label(text="", icon="OUTLINER_DATA_MESH")
                        row.prop(active_object.data, "name", text="")
                        row = col.row(align=True)
                        
                    uv_maps = active_object.data.uv_layers
                    if duckx_tools.uvmaps == True:
                        if uv_maps:
                            for i, uv_map in enumerate(uv_maps):
                                if len(active_object.data.uv_layers) >= 4:
                                    if active_object.data.uv_layers.active == uv_map:
                                        row.operator("duckx_tools.active_uv_map_operator", text=str(i), depress=True).action = "duckx_uvset:>" + str(i) + ":>" + uv_map.name
                                    else:
                                        row.operator("duckx_tools.active_uv_map_operator", text=str(i)).action = "duckx_uvset:>" + str(i) + ":>" + uv_map.name
                                else:
                                    if active_object.data.uv_layers.active == uv_map:
                                        row.operator("duckx_tools.active_uv_map_operator", text=uv_map.name, depress=True).action = "duckx_uvset:>" + str(i) + ":>" + uv_map.name
                                    else:
                                        row.operator("duckx_tools.active_uv_map_operator", text=uv_map.name).action = "duckx_uvset:>" + str(i) + ":>" + uv_map.name
                            row = col.row(align=True)
                        else:
                            row.operator("duckx_tools.active_uv_map_operator", text="New UV Map").action = "new"
                            row = col.row(align=True)
                    
                    if duckx_tools.custom_props == True:
                        if active_object.keys():
                            row.scale_y = 0.7
                            row.label(text="Custom Properties :")
                            if duckx_tools.filter_props != "":
                                for key in active_object.keys():
                                    if key in duckx_tools.filter_props:
                                        row = col.row()
                                        row.scale_y = 0.7
                                        row.active = False
                                        row.label(text=key + " : " + str(active_object[key]))
                            else:
                                for key in active_object.keys():
                                    row = col.row()
                                    row.scale_y = 0.7
                                    row.active = False
                                    row.label(text=key + " : " + str(active_object[key]))
            
        if duckx_tools.tri_count == True:
            row = layout.row()
            row.alignment = 'LEFT'
            row.label(text="", icon="MOD_TRIANGULATE")
            row.label(text = str(func_core.get_triangle()))
            #row.popover("VIEW3D_PT_PopTriangleMenu", text="-50%")
            #row.label(text = str(func_core.get_triangle()))

        if duckx_tools.tri_track == True:
            row = layout.row(align=True)
            row.operator("duckx_tools.tri_cal_operator", text="", icon="SHADERFX")
            row.scale_x = 0.5
            row.prop(duckx_tools, "tri_cal_factor", text="")
            row.scale_x = 1
            row.prop(duckx_tools, "tri_sum", text="")
            if triangles_tools.tracking == True:
                total_triangles = sum(count for _, count in triangles_tools.objects) 
                if total_triangles >= int(duckx_tools.tri_sum):
                    row = layout.row()
                    row.alert = True
                    row.scale_y = 2
                    selected_objects = context.selected_objects
                    for obj in selected_objects:
                        if obj.type == "MESH":
                            for index in range(len(triangles_tools.objects)):
                                if obj.name == triangles_tools.objects[index][0]:
                                    num_triangles = 0
                                    mesh = obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
                                    num_triangles += sum(len(p.vertices) - 2 for p in mesh.polygons)
                                    triangles_tools.objects[index] = [obj.name, num_triangles]
                                    print(triangles_tools.objects[index])
                    row.operator("duckx_tools.tri_tracker_operator", text=str(total_triangles), icon="PIVOT_BOUNDBOX")
                else:
                    triangles_tools.tracking = False
                    func_core.message_box("Complete", "Triangles Tracking", "FUND")
            else:
                row = layout.row()
                row.operator("duckx_tools.tri_tracker_operator", text="Triangles Tracker", icon="SHADING_BBOX")
                row = layout.row()
        

        row = layout.row()
        row.prop(context.scene.tool_settings, "use_transform_correct_face_attributes", text="Correct Face Attributes", icon="UV")
        if  bpy.context.scene.tool_settings.use_transform_correct_face_attributes == True:
            row.prop(context.scene.tool_settings, "use_transform_correct_keep_connected", text="", icon="LINKED")

        #row = layout.row()
        row = layout.row(align=True) # Create a row with alignment
        row.alignment = "CENTER"
        row.prop(duckx_tools, "tabs_menu", text="", expand=True) # Tabs, no expand
        row.scale_x = 2

        #Mesh Tab
        if duckx_tools.tabs_menu == "mesh":
            layout = self.layout
            row = layout.row()
            row.label(text="Mesh :")
            row = layout.row()
            row.operator("duckx_tools.orienglobal_operator", icon="ORIENTATION_GLOBAL")
            row.operator("duckx_tools.orienselect_operator", icon="OBJECT_ORIGIN")
            row = layout.row()
            row.operator("duckx_tools.addempty_operator", icon="EMPTY_ARROWS")
            if context.mode == "EDIT_MESH":
                row = layout.row()
                row.operator("duckx_tools.utilities_operator", text="Scale Zero", icon="DECORATE").action = "Scale 0"
                row.operator("duckx_tools.move_vert_to_active_operator", text="Vx At Last", icon="ARROW_LEFTRIGHT")
                row = layout.row()
                row.operator("duckx_tools.utilities_operator", text="Deparate", icon="DUPLICATE").action ="Deparate"
                row.operator("duckx_tools.orien_and_pivot_operator", text="Pivot", icon="PIVOT_CURSOR")
                row = layout.row()
                row.operator("duckx_tools.utilities_operator", text="Origin to selection", icon="PIVOT_BOUNDBOX").action ="Origin to selection"
                row = layout.row()
                row.operator("duckx_tools.utilities_operator", text="Boundary Sharp", icon="MATPLANE").action ="Boundary Sharp"
                row = layout.row()
                row.operator("duckx_tools.invert_in_loose_parts_operator", text="Invert In Loose Parts", icon="MOD_EXPLODE")
                #row = layout.row()
                #row.operator("duckx_tools.select_by_distance_operator", text="Select By Distance", icon="FIXED_SIZE")
                
                #Merge Tools
                box = layout.box()
                row = box.row()
                if duckx_tools.merge_tools != False:
                    row.operator("duckx_tools.toggle_prop_operator", text="", icon="TRIA_DOWN").prop_name = "merge_tools"
                    row.label(text="Merge")
                    row = box.row()
                    if len(selected_objects) != 0 and active_object.type == "MESH":
                        row.enabled = True
                    else:
                        row.enabled = False
                    try:
                        row.operator("duckx_tools.merge_by_size_operator", text="Face", icon="LIGHTPROBE_PLANAR").action = "face"
                    except:
                        row.operator("duckx_tools.merge_by_size_operator", text="Face", icon="LIGHTPROBE_PLANE").action = "face"
                    row.operator("duckx_tools.merge_by_size_operator", text="Edge", icon="SNAP_MIDPOINT").action = "edge"
                else:
                    row.operator("duckx_tools.toggle_prop_operator", text="", icon="TRIA_RIGHT").prop_name = "merge_tools"
                    row.label(text="Merge")
                
            #Flip Tools
            box = layout.box()
            row = box.row()
            if duckx_tools.flip_tools_toggle != False:
                row.operator("duckx_tools.toggle_prop_operator", text="", icon="TRIA_DOWN").prop_name = "flip_tools_toggle"
                row.label(text="Flip")
                row = box.row()
                if len(selected_objects) != 0 and active_object.type == "MESH":
                    row.enabled = True
                else:
                    row.enabled = False
                row.operator("duckx_tools.fliptools_operator", text="X", icon="AXIS_SIDE").axis = "X"
                row.operator("duckx_tools.fliptools_operator", text="Y", icon="AXIS_FRONT").axis = "Y"
                row.operator("duckx_tools.fliptools_operator", text="Z", icon="AXIS_TOP").axis = "Z"
            else:
                row.operator("duckx_tools.toggle_prop_operator", text="", icon="TRIA_RIGHT").prop_name = "flip_tools_toggle"
                row.label(text="Flip")

            #Align Tools
            box = layout.box()
            row = box.row()
            if duckx_tools.movex_tools != False:
                row.operator("duckx_tools.toggle_prop_operator", text="", icon="TRIA_DOWN").prop_name = "movex_tools"
                row.label(text="Align")
                col = box.column(align=True)
                col.label(text="Align To Active")
                row = col.row(align=True)
                row.alignment = "CENTER"
                row.scale_y = 1.5
                row.scale_x = 5
                bt = row.operator("duckx_tools.align_to_active_operator", text="", icon_value=icon_reg.iconLib("giz_X"))
                bt.axis = "x"
                bt = row.operator("duckx_tools.align_to_active_operator", text="", icon_value=icon_reg.iconLib("giz_Y"))
                bt.axis = "y"
                bt = row.operator("duckx_tools.align_to_active_operator", text="", icon_value=icon_reg.iconLib("giz_Z"))
                bt.axis = "z"
                col = box.column(align=True)
                row = col.row(align=True)
                row.label(text="Move From Active")
                row = col.row(align=True)
                row.scale_x = 5
                row.alignment = "CENTER"
                bt = row.operator("duckx_tools.movex_tools_operator", text="", icon_value=icon_reg.iconLib("giz_X"))
                bt.move_axis = "x"
                bt = row.operator("duckx_tools.movex_tools_operator", text="", icon_value=icon_reg.iconLib("giz_Y"))
                bt.move_axis = "y"
                bt = row.operator("duckx_tools.movex_tools_operator", text="", icon_value=icon_reg.iconLib("giz_Z"))
                bt.move_axis = "z"
                

                
            else:
                row.operator("duckx_tools.toggle_prop_operator", text="", icon="TRIA_RIGHT").prop_name = "movex_tools"
                row.label(text="Align")

            #Shape Tools
            box = layout.box()
            row = box.row()
            if duckx_tools.shape_tools != False:
                row.operator("duckx_tools.toggle_prop_operator", text="", icon="TRIA_DOWN").prop_name = "shape_tools"
                row.label(text="Shape")
                row = box.row()
                # if len(selected_objects) != 0 and active_object.type == "MESH":
                #     row.enabled = True
                # else:
                #     row.enabled = False
                row.operator("duckx_tools.convex_tools_operator", text="Convex X", icon="MESH_ICOSPHERE")
                row.operator("duckx_tools.box_from_mesh_operator", text="Box Mesh", icon="MESH_CUBE")
                row = box.row()
                row.operator("duckx_tools.mesh_to_box_operator", text="Mesh To Box", icon="MESH_CUBE")
            else:
                row.operator("duckx_tools.toggle_prop_operator", text="", icon="TRIA_RIGHT").prop_name = "shape_tools"
                row.label(text="Shape")
                
            #Objects Display
            box = layout.box()
            row = box.row()
            if duckx_tools.object_data != False:
                row.operator("duckx_tools.toggle_prop_operator", text="", icon="TRIA_DOWN").prop_name = "object_data"
                row.label(text="Object Data")
                row = box.row()
                row.label(text="Color")
                row = box.row()
                row.scale_x = 0.5
                if active_object:
                    row.prop(context.object, "color", text="")
                row.operator("duckx_tools.object_colors", text="", icon="TRIA_RIGHT").action = "pick"
                row.prop(duckx_tools, "obj_color", text="")
                row.scale_x = 2
                row.operator("duckx_tools.object_colors", text="", icon="SHADERFX").action = "set"
                row = box.row()
                row.operator("duckx_tools.object_colors", text="Select Similar Color").action = "select"
                
                #Objects Wireframe
                #box = layout.box()
                row = box.row()
                row.label(text="Wireframe")
                row = box.row()
                row.operator("duckx_tools.object_wire", text="Show/Hide").action = "toggle"
                row.operator("duckx_tools.object_wire", text="Select").action = "select"
                row = box.row()
                row.label(text="Properties")
                row = box.row()
                row.operator("duckx_tools.del_custom_prop_operator", text="Delete All Custom Properties", icon="CON_TRANSFORM")
            else:
                row.operator("duckx_tools.toggle_prop_operator", text="", icon="TRIA_RIGHT").prop_name = "object_data"
                row.label(text="Object Data")
            
            #Modifiers Tools
            box = layout.box()
            row = box.row()
            if duckx_tools.modifiers_tools != False:
                row.operator("duckx_tools.toggle_prop_operator", text="", icon="TRIA_DOWN").prop_name = "modifiers_tools"
                row.label(text="Modifiers")
                row = box.row()
                row.prop(duckx_tools, "mod_name", text="Name")
                row.operator("duckx_tools.del_modifiers_operator", text="", icon="TRASH").action = "by_name"
            else:
                row.operator("duckx_tools.toggle_prop_operator", text="", icon="TRIA_RIGHT").prop_name = "modifiers_tools"
                row.label(text="Modifiers")

                

            #Objects Data
            box = layout.box()
            row = box.row()
            if duckx_tools.mesh_data != False:
                row.operator("duckx_tools.toggle_prop_operator", text="", icon="TRIA_DOWN").prop_name = "mesh_data"
                row.label(text="Mesh Data")
                row = box.row()
                row.operator("duckx_tools.duplicate_blend_operator", text="Duplicate Blend", icon="MOD_ARRAY")
                row = box.row()
                row.label(text="Rename")
                row = box.row()
                row.label(text="Object")
                if duckx_tools.name_to_mesh != False:
                    row.operator("duckx_tools.toggle_prop_operator", text="", icon="TRIA_RIGHT").prop_name = "name_to_mesh"
                else:
                    row.operator("duckx_tools.toggle_prop_operator", text="", icon="TRIA_LEFT").prop_name = "name_to_mesh"
                row.label(text="Mesh")
                row.operator("duckx_tools.set_mesh_name_operator", text="", icon="SHADERFX")
            else:
                row.operator("duckx_tools.toggle_prop_operator", text="", icon="TRIA_RIGHT").prop_name = "mesh_data"
                row.label(text="Mesh Data")
        
        #UV Tools Tab
        elif duckx_tools.tabs_menu == "uv":
            row = layout.row()
            row.label(text="UV :")
            if context.mode == "EDIT_MESH":
                row = layout.row(align=True)
                row.operator("duckx_tools.invert_seam_operator", text="Invert Seam", icon="SHADERFX")
                box = layout.box()
                row = box.row()
                row.label(text="UV Rotation")
                row.prop(duckx_tools, "uv_angle", text="")
                row.operator("duckx_tools.uvrotation_operator", text="", icon="FILE_REFRESH").angle = duckx_tools.uv_angle
                row = box.row()
                row.operator("duckx_tools.uvrotation_operator", text="-90°").angle = -90
                row.operator("duckx_tools.uvrotation_operator", text="+90°").angle = 90
                row.operator("duckx_tools.uvrotation_operator", text="-45°").angle = -45
                row.operator("duckx_tools.uvrotation_operator", text="+45°").angle = 45
                row = box.row()
                row.operator("duckx_tools.uvrotation_operator", text="180°").angle = 180

            
        
        #Macro
        if duckx_tools.tabs_menu == "macro":
            layout = self.layout
            row = layout.row()
            row.label(text="Macro :")
            
            #Select from Index
            box = layout.box()
            row = box.row()
            if duckx_tools.select_mesh_from_index != False:
                row.operator("duckx_tools.toggle_prop_operator", text="", icon="TRIA_DOWN").prop_name = "select_mesh_from_index"
                row.label(text="Select from index")
                col = box.column(align=True)
                row = col.row(align=True)
                row.prop(duckx_tools, "select_type", expand=True)
                col.prop(duckx_tools, "select_index_number")
                row = box.row(align=True)
                row.operator("duckx_tools.select_from_index_operator", text="Select")
            else:
                row.operator("duckx_tools.toggle_prop_operator", text="", icon="TRIA_RIGHT").prop_name = "select_mesh_from_index"
                row.label(text="Select from index")
            
            #Run Script
            box = layout.box()
            row = box.row()
            if duckx_tools.run_script != False:
                row.operator("duckx_tools.toggle_prop_operator", text="", icon="TRIA_DOWN").prop_name = "run_script"
                row.label(text="Run Script")
                col = box.column(align=True)
                texts = bpy.data.texts
                for text in texts:
                    col.operator("duckx_tools.run_script_operator", text=text.name).file_name = text.name
            else:
                row.operator("duckx_tools.toggle_prop_operator", text="", icon="TRIA_RIGHT").prop_name = "run_script"
                row.label(text="Run Script")

        #File and Render
        if duckx_tools.tabs_menu == "file_render":
            layout = self.layout
            row = layout.row()
            row.label(text="File and Render :")
            box = layout.box()
            row = box.row()
            row.label(text="Collection Export")
            row = box.row()
            row.prop(duckx_tools, "export_path", text="")
            row = box.row()
            row.operator("duckx_tools.collection_export_operator", text="Add").action = "add_data"
            row.operator("duckx_tools.collection_export_operator", text="Remove").action = "remove_data"
            row.operator("duckx_tools.collection_export_operator", text="Export").action = "export"

            active_collection = bpy.context.view_layer.active_layer_collection
            collection_name = active_collection.name
            export_data = func_core.get_collection_custom_property(collection_name, "Duckx Export Data")
            if not export_data is None:
                col = box.column(align=True)
                row = col.row()
                col.label(text="Export Data")
                row = col.row()
                row.label(icon=func_core.get_collection_icon_by_color_tag(collection_name))
                row.label(text=collection_name)
                row = col.row()
                row.alignment = "LEFT"
                row.active = False
                row.label(icon="BLANK1")
                export_data = func_core.string_to_list(export_data)
                row.label(text="File :")
                row.label(text=export_data[0])
                row = col.row()
                row.alignment = "LEFT"
                row.active = False
                row.label(icon="BLANK1")
                row.label(text="Path :")
                row.label(text=export_data[1])

        #Setting Tab
        elif duckx_tools.tabs_menu == "setting":
            row = layout.row()
            row.label(text="Setting :")
            box = layout.box()
            col = box.column(heading="Object Info", align=True)
            col.prop(duckx_tools, "object_name")
            col.prop(duckx_tools, "mesh_name")
            col.prop(duckx_tools, "uvmaps")
            col.prop(duckx_tools, "custom_props")
            col.prop(duckx_tools, "filter_props", text="Filter")
            box = layout.box()
            col = box.column(heading="", align=True)
            col.prop(duckx_tools, "groups_panel")
            col.prop(duckx_tools, "decals_panel")
            box = layout.box()
            col = box.column(heading="Triangles", align=True)
            col.prop(duckx_tools, "tri_count")
            col.prop(duckx_tools, "tri_track")
            box = layout.box()
            row = box.row()
            row.label(text="Keymap")
            row = box.row()
            row.label(text="Press D at View3D, UV")
            if duckx_tools.auto_keymap == True:
                row.operator("duckx_tools.toggle_prop_operator", text="", icon="CHECKBOX_HLT").prop_name = "auto_keymap"
            else:
                row.operator("duckx_tools.toggle_prop_operator", text="", icon="CHECKBOX_DEHLT").prop_name = "auto_keymap"
            row = box.row()
            row.operator("duckx_tools.duckx_keymap_operator", text="Add").action = "add"
            row.operator("duckx_tools.duckx_keymap_operator", text="Remove").action = "remove"
            row = layout.row()
            row.template_icon(icon_reg.iconLib("duckx_symbol_type_frame_bg"), scale=5)
        
class VIEW3D_PT_Duckx_DecalsTools(Panel):
    bl_idname = "VIEW3D_PT_decals_panel"
    bl_label = "Decals Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "🦆"

    @classmethod
    def poll(cls, context):
        return context.scene.duckx_tools.decals_panel
    
    def draw(self, context):
        scene = context.scene
        duckx_tools = scene.duckx_tools 

        layout = self.layout
        box = layout.box()
        row = box.row()
        row.label(text = "Ring", icon_value=icon_reg.iconLib("decal_ring"))
        row.prop(duckx_tools, "decal_ring_set", text="", icon="PREFERENCES")
        if duckx_tools.decal_ring_set != False:
            row = box.row()
        row = box.row(align=True)
        row.scale_y = 1.5
        row.scale_x = 5
        row.alignment = "CENTER"
        row.operator("duckx_tools.decal_ring_operator", text="", icon_value=icon_reg.iconLib("giz_X")).decalAxis = "X"
        row.operator("duckx_tools.decal_ring_operator", text="", icon_value=icon_reg.iconLib("giz_Y")).decalAxis = "Y"
        row.operator("duckx_tools.decal_ring_operator", text="", icon_value=icon_reg.iconLib("giz_Z")).decalAxis = "Z"
        row = box.row(align=True)
        row.operator("duckx_tools.uv_position_random_operator", text="Random X").action = "x"
        row.operator("duckx_tools.uv_position_random_operator", text="Random Y").action = "y"
        
            
        
class VIEW3D_PT_Duckx_Groups(Panel):
    bl_idname = "VIEW3D_PT_duckx_groups_panel"
    bl_label = "Groups"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "🦆"

    @classmethod
    def poll(cls, context):
        return context.scene.duckx_tools.groups_panel
    
    def draw(self, context):
        scene = context.scene
        duckx_tools = scene.duckx_tools  

        layout = self.layout
        row = layout.row(align=True)
        row.alignment = "CENTER"
        #row.label(text = "Groups")

        tabs = func_core.string_to_list(duckx_tools.group_lib)
        #print(tabs)
        if len(tabs) > 0:
            for i, tab in enumerate(tabs):
                #print(tab)
                tab = row.operator("duckx_tools.group_tools_operator", text=str(i) if len(tabs) > 4 else tabs[i][0], depress=True if i == duckx_tools.tab_active else False)
                tab.action = "active_tab"
                tab.tab_index = i
                
            row.operator("duckx_tools.group_tools_operator", text="", icon="ADD").action = "add_tab"
            box = layout.box()
            row = box.row(align=True)
            #for groups in tabs[duckx_tools.group_active]:
            if group_tools.edit_tab_name == True:
                row.prop(duckx_tools, "group_tab_name", text="")
                row.operator("duckx_tools.group_tools_operator", text="", icon="CHECKMARK").action = "rename_yes"
                row.operator("duckx_tools.group_tools_operator", text="", icon="PANEL_CLOSE").action = "rename_cancel"
            else:
                row.label(text=tabs[duckx_tools.tab_active][0])
                row.operator("duckx_tools.group_tools_operator", text="", icon="OUTLINER_DATA_GP_LAYER").action = "rename_tab"
            row.operator("duckx_tools.group_tools_operator", text="", icon="TRASH").action = "del_tab"
            col = box.column(align=True)
            if len(tabs[duckx_tools.tab_active][1]) > 0:
                for i in range(len(tabs[duckx_tools.tab_active][1])):
                    row = col.row(align=True)
                    group_name = ", ".join(tabs[duckx_tools.tab_active][1][i][1])
                    group = row.operator("duckx_tools.group_tools_operator", text=group_name, icon="OBJECT_DATA" if tabs[duckx_tools.tab_active][1][i][0] == "object" else "OUTLINER_COLLECTION")
                    group.action = "active_group"
                    group.index = i
                    append_group = row.operator("duckx_tools.group_tools_operator", text="", icon="ADD")
                    append_group.action = "append_to_group"
                    append_group.index = i
                    remove_group = row.operator("duckx_tools.group_tools_operator", text="", icon="REMOVE")
                    remove_group.action = "remove_from_group"
                    remove_group.index = i
                    del_group = row.operator("duckx_tools.group_tools_operator", text="", icon="TRASH")
                    del_group.action = "del_group"
                    del_group.index = i
            row = box.row(align=True)
            row.alignment = "CENTER"
            row.scale_x = 2
            #row.operator("duckx_tools.group_tools_operator", text="", icon="ADD").action = "append"
            row.popover("VIEW3D_PT_add_group_menu", text="", icon="ADD")
        else:
            row.operator("duckx_tools.group_tools_operator", text="", icon="ADD").action = "add_tab"
            #row.operator("duckx_tools.group_tools_operator", text="0").action = "tab"

class VIEW3D_PT_Duckx_AddGroupMenu(Panel):
    bl_label = "Add Group"
    bl_idname = "VIEW3D_PT_add_group_menu"
    bl_options = {'INSTANCED'}
    bl_space_type = 'VIEW_3D' 
    bl_region_type = 'WINDOW'

    def draw(self, context):
        scene = context.scene
        duckx_tools = scene.duckx_tools
        layout = self.layout
        row = layout.row(align=True)
        row.operator("duckx_tools.group_tools_operator", text="Collection", icon="OUTLINER_COLLECTION").action = "add_coll_group"   
        row.operator("duckx_tools.group_tools_operator", text="Object", icon="OBJECT_DATA").action = "add_obj_group"   

        

class DuckXMenu(Menu):
    bl_idname = "OBJECT_MT_duckx_tools"
    bl_label = "DuckX Tools"

    def draw(self, context):
        layout = self.layout

        if not context.area.type == 'IMAGE_EDITOR':
            if bpy.context.scene.tool_settings.use_transform_correct_face_attributes == True:
                layout.operator("duckx_tools.utilities_operator", text="Correct Face", icon="CHECKBOX_HLT").action = "Correct Face Att"
            else:
                layout.operator("duckx_tools.utilities_operator", text="Correct Face", icon="CHECKBOX_DEHLT").action = "Correct Face Att"
            layout.operator("duckx_tools.orienglobal_operator", text="Orientation Global", icon="OBJECT_ORIGIN")
            
            if context.mode == 'EDIT_MESH':
                layout.operator("duckx_tools.orienselect_operator", text="Orientation Select", icon="TRACKER")
                layout.operator("duckx_tools.utilities_operator", text="Scale 0", icon="DECORATE").action ="Scale 0"
                layout.operator("duckx_tools.orien_and_pivot_operator", text="Edge Pivot Align", icon="SNAP_MIDPOINT")
                layout.operator("duckx_tools.utilities_operator", text="Boundary Sharp", icon="MATPLANE").action ="Boundary Sharp"
                layout.operator("duckx_tools.utilities_operator", text="Delete Loose Part", icon="PANEL_CLOSE").action ="Delete Loose Part"
                layout.operator_menu_enum("duckx_tools.remove_loop_ring_operator", property="action", text="Remove Ring Loop", icon="PANEL_CLOSE")
                layout.operator("duckx_tools.move_vert_to_active_operator", text="Move Vx At Last", icon="ARROW_LEFTRIGHT")
                layout.separator()
                layout.label(text="Merge by size")
                try:
                    layout.operator("duckx_tools.merge_by_size_operator", text="Face", icon="LIGHTPROBE_PLANAR").action = "face"
                except:
                    layout.operator("duckx_tools.merge_by_size_operator", text="Face", icon="LIGHTPROBE_PLANE").action = "face"
                layout.operator("duckx_tools.merge_by_size_operator", text="Edge", icon="SNAP_MIDPOINT").action = "edge"
                layout.separator()
                layout.label(text="Dimension")
                layout.operator("duckx_tools.utilities_operator", text="Edge Length", icon="FIXED_SIZE").action = "Edge Length"
                
            layout.separator()
            layout.operator_menu_enum("duckx_tools.object_wire", property="action", text="Wirew", icon="MESH_ICOSPHERE")
        else:
            layout.operator("duckx_tools.utilities_operator", text="A Scale Zero", icon="DECORATE").action ="Scale 0"
            layout.operator("duckx_tools.uvpadding_operator", text="+ " + "Padding", icon="MOD_EXPLODE").action = "more"
            layout.operator("duckx_tools.uvpadding_operator", text="- " + "Padding", icon="MOD_EXPLODE").action = "less"
            layout.operator("duckx_tools.uv_unwarp_here_operator", text="Unwarp Here", icon="UV")
            layout.operator("duckx_tools.uvrotation_operator", text="Q -90°").angle = -90
            layout.operator("duckx_tools.uvrotation_operator", text="E +90°").angle = 90
                
        #Console
        layout.separator()
        layout.operator("duckx_tools.console_command_operator", text="Console", icon="CONSOLE")


def draw_duckx_operator(self, context):
    layout = self.layout
    if  bpy.context.scene.tool_settings.use_transform_correct_face_attributes == True:
        layout.prop(context.scene.tool_settings, "use_transform_correct_face_attributes", text="", icon="SEQUENCE_COLOR_04")
    else:
        layout.prop(context.scene.tool_settings, "use_transform_correct_face_attributes", text="", icon="SEQUENCE_COLOR_09")
    layout.prop(context.scene.tool_settings, "use_transform_correct_keep_connected", text="", icon="LINK_BLEND")

classes = [VIEW3D_PT_Duckx_MainPanel, VIEW3D_PT_Duckx_DecalsTools, VIEW3D_PT_Duckx_Groups, VIEW3D_PT_Duckx_AddGroupMenu, DuckXMenu]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_HT_tool_header.append(draw_duckx_operator)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.VIEW3D_HT_tool_header.remove(draw_duckx_operator)