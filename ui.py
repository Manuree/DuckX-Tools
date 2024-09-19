import bpy


from . import icon_reg
from . import properties
from . import setting
from .operators import func_core
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
        row.scale_x = 0.85
        row.label(text="", icon_value=icon_reg.iconLib("logo_D"))
        row.label(text="", icon_value=icon_reg.iconLib("logo_U"))
        row.label(text="", icon_value=icon_reg.iconLib("logo_C"))
        row.label(text="", icon_value=icon_reg.iconLib("logo_K"))
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
        
        # if duckx_tools.uvmap_active == True:
        #     row = layout.row()
        #     if selected_objects:
        #         try:
        #             if active_object.type == 'MESH' and len(selected_objects) != 0:
        #                 uvmaps = active_object.data.uv_layers
        #                 for uvmap in uvmaps:
        #                     if active_object.data.uv_layers.active.name == uvmap.name:
        #                         row.prop(uvmap, "name", text="")
        #                         row.prop(uvmap, "active_render", text="", icon="RESTRICT_RENDER_OFF")
        #                         row.operator("duckx_tools.active_uv_map_operator", text="", icon="FILE_REFRESH").action = "toggle"
        #                         row = layout.row()
        #         except:
        #             print("No active Object")
        row = layout.row()
        row.prop(context.scene.tool_settings, "use_transform_correct_face_attributes", text="Correct Face Attributes", icon="STICKY_UVS_VERT")
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

            #Transfrom Tools
            box = layout.box()
            row = box.row()
            if duckx_tools.movex_tools != False:
                row.operator("duckx_tools.toggle_prop_operator", text="", icon="TRIA_DOWN").prop_name = "movex_tools"
                row.label(text="Transfrom Tools")
                row = box.row(align=True)
                row.label(text="Move")
                row = box.row(align=True)
                row.scale_y = 0.1
                row.enabled = False
                row.label(text="Ctrl Click for invert axis")
                row = box.row(align=True)
                row.scale_y = 1.5
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
                row.label(text="Transfrom Tools")

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

            box = layout.box()
            obj = bpy.context.active_object
            selected_objects = bpy.context.selected_objects
            if selected_objects:
                if obj:
                    if obj.type == 'MESH':
                        uvmaps = obj.data.uv_layers
                        for uvmap in uvmaps:
                            if obj.data.uv_layers.active.name == uvmap.name:
                                row = box.row()
                                row.label(text="UV Map Active : " + uvmap.name)
                                row.prop(uvmap, "active_render", text="", icon="RESTRICT_RENDER_OFF")
                    else:
                        row = box.row()
                        row.label(text="Please Select Mesh")
                
            row = box.row()
            row.prop(duckx_tools, "uvmap_set_type", expand=True)
            row.scale_x = 2
            if duckx_tools.uvmap_set_type == "name":
                row.prop(duckx_tools, "uvmap_name", text="")
            elif duckx_tools.uvmap_set_type == "index":
                row.prop(duckx_tools, "uvmap_index", text="")
            row = box.row()
            row.operator("duckx_tools.active_uv_map_operator", text="Active").action = "set"
            row.operator("duckx_tools.active_uv_map_operator", text="New").action = "new"
            row.operator("duckx_tools.active_uv_map_operator", text="Rename").action = "rename"
            row.enabled = True
            row.operator("duckx_tools.active_uv_map_operator", text="Delete").action = "del"
            row = box.row()
            row.operator("duckx_tools.uvrotation_operator", text="Delete")
        
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
            col.prop(duckx_tools, "show_hide_panel")
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
        
class VIEW3D_PT_TriangleMenu(Panel):
    bl_label = "Triangle"
    bl_idname = "VIEW3D_PT_triangle_menu"
    bl_options = {'INSTANCED'}
    bl_space_type = 'VIEW_3D' 
    bl_region_type = 'WINDOW'

    def draw(self, context):
        scene = context.scene
        duckx_tools = scene.duckx_tools        

        layout = self.layout
        row = layout.row()
        row.label(text = str(func_core.selectedObjectsVex()))

class VIEW3D_PT_DecalsTools(Panel):
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
        
            
        
class VIEW3D_PT_ShowHide(Panel):
    bl_idname = "VIEW3D_PT_show_hide_panel"
    bl_label = "Show and Hide"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "🦆"

    @classmethod
    def poll(cls, context):
        return context.scene.duckx_tools.show_hide_panel
    
    def draw(self, context):
        scene = context.scene
        duckx_tools = scene.duckx_tools  

        layout = self.layout
        row = layout.row()
        row.label(text = "Groups")
        box = layout.box()
        if duckx_tools.list_groups != "" and duckx_tools.list_groups != "[]":
            groups = func_core.string_to_list(duckx_tools.list_groups)
            for i in range(len(groups)):
                row = box.row(align=True)
                #row.alignment = "CENTER"
                show = row.operator("duckx_tools.show_hide_operator", text=str(i), icon="OBJECT_DATA")
                show.action = "show"
                show.index = i
                add = row.operator("duckx_tools.show_hide_operator", text="", icon="ADD")
                add.action = "add"
                add.index = i
                remove = row.operator("duckx_tools.show_hide_operator", text="", icon="REMOVE")
                remove.action = "remove"
                remove.index = i
                de = row.operator("duckx_tools.show_hide_operator", text="", icon="TRASH")
                de.action = "del"
                de.index = i
        row = box.row(align=True)
        row.alignment = "CENTER"
        row.scale_x = 2
        row.operator("duckx_tools.show_hide_operator", text="", icon="ADD").action = "append"


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

classes = [VIEW3D_PT_Duckx_MainPanel, VIEW3D_PT_TriangleMenu, VIEW3D_PT_DecalsTools, VIEW3D_PT_ShowHide, DuckXMenu]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
