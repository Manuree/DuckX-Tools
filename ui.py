import bpy
from bpy.types import Panel
from bpy.types import Menu
from bpy.types import Scene
from bpy.types import Header
from bpy.props import StringProperty

#from .operators import func_core
from .icon_reg import *

panel_layout = {}
expand_panel_layout = {}

def draw_expand_panel(self, context, layout, text="", properties=None):
    # สร้าง entry พร้อมค่าเริ่มต้น (รวม "tab" กัน KeyError)
    entry = expand_panel_layout.setdefault(text, {
        "draw_func": None,
        "expand": False,
        "tab": None,  # ถ้าไม่กำหนด tab จะถือว่าให้แสดงทุก tab
    })

    # กรองด้วย tab ก่อน "ยังไม่ต้องสร้าง UI" ถ้าไม่ตรง
    tabs_menu = getattr(context.scene.duckx_tools, "tabs_menu", None)
    required_tab = entry.get("tab")
    if required_tab is not None and tabs_menu != required_tab:
        return None

    # ---- วาด UI ต่อเมื่อผ่านเงื่อนไขแล้วเท่านั้น ----
    box = layout.box()
    row = box.row(align=True)
    row.scale_y = 0.75
    row.alignment = "LEFT"

    icon = 'TRIA_DOWN' if entry["expand"] else 'TRIA_RIGHT'

    op = row.operator("duckx_tools.duckx_expand_panel", text=text, icon=icon, emboss=False)
    op.panel_name = text  # ส่งชื่อ panel ผ่าน property

    if entry["expand"] and entry["draw_func"]:
        entry["draw_func"](self, context, box, properties)

    return box

def draw_panel(self, context, layout, text="", properties=None):
    if text not in panel_layout:
        panel_layout[text] = {"draw_func": None}
    if panel_layout[text]["draw_func"]:
        panel_layout[text]["draw_func"](self, context, layout, properties)
    return layout

def add_panel(panel_name, draw_func):
    panel_layout[panel_name] = {
        "draw_func": draw_func,
    }
    print(f"--- Panel '{panel_name}' added")

def add_expand_panel(panel_name, draw_func, tab="MESH"):
    """
    เพิ่ม expand panel เข้าไปในระบบ

    Parameters:
        panel_name (str): ชื่อ panel
        draw_func (callable): ฟังก์ชันวาด UI
        tab (str): ประเภท tab ที่ panel นี้จะอยู่ (ค่าเริ่มต้น "MESH")
                   ตัวเลือกเช่น "MESH", "UV", "INS", "UTIL", "VIEW", "FILE_RENDER", "SETTING"
    """
    expand_panel_layout[panel_name] = {
        "draw_func": draw_func,
        "tab":tab,
        "expand": False
    }
    print(f"--- Expand Panel '{panel_name}' added")




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
        row.label(text="", icon_value=iconLib("logo_D"))
        row.label(text="", icon_value=iconLib("logo_U"))
        row.label(text="", icon_value=iconLib("logo_C"))
        row.label(text="", icon_value=iconLib("logo_K"))
        row.label(text="", icon_value=iconLib("logo_X"))
        #layout.label(text="Tools")
        

    def draw(self, context):
        scene = context.scene
        props = scene.duckx_tools
        active_object = context.active_object      

        layout = self.layout

        # Objects information
        if props.custom_props and active_object:
            # เอาเฉพาะคีย์ custom prop จริง ๆ (ตัดพวก _RNA_UI ออก)
            keys = [k for k in active_object.keys() if not k.startswith("_")]

            if keys:
                box = layout.box()
                col = box.column()
                row = col.row()
                row.scale_y = 0.7
                row.label(text="Custom Properties :")
                if props.filter_props != "":
                    for key in active_object.keys():
                        if key in props.filter_props:
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
       
        if props.uvmaps:
            draw_panel(self, context, layout, "UV_Map_Manager", props)

        # Correct Face Attributes
        row = layout.row(align=True)
        row.scale_y = 1.5
        row.prop(context.scene.tool_settings, "use_transform_correct_face_attributes", text="Correct Face Attributes", icon="UV")
        if  bpy.context.scene.tool_settings.use_transform_correct_face_attributes == True:
            row.prop(context.scene.tool_settings, "use_transform_correct_keep_connected", text="", icon="LINKED")

        # Create a row for the tabs
        row = layout.row(align=True) # Create a row with alignment
        row.alignment = "CENTER"
        row.prop(props, "tabs_menu", text="", expand=True) # Tabs, no expand
        row.scale_x = 2


        if props.tabs_menu == "MESH":
            # Draw Orientation Tools
            if panel_layout:
                row = layout.row(align=True)
                draw_panel(self, context, row, "Orient Tools", props)
                row = layout.row(align=True)
                draw_panel(self, context, row, "Add_Empty", props)
                draw_panel(self, context, row, "Tranfer_From_Active", props)
                row = layout.row(align=True)
                draw_panel(self, context, row, "Scale_Zero", props)
                row = layout.row(align=True)
                draw_panel(self, context, row, "Boundary_Tools", props)

            if expand_panel_layout:
                for panel_name in expand_panel_layout:
                    draw_expand_panel(self, context, layout, panel_name, props)

        elif props.tabs_menu == "UV":
            row = layout.row(align=True)
            draw_panel(self, context, row, "Invert Seam", props)
            row = layout.row(align=True)
            draw_panel(self, context, row, "UV Rotation", props)

        elif props.tabs_menu == "INS":
            pass
        elif props.tabs_menu == "UTIL":
            if expand_panel_layout:
                for panel_name in expand_panel_layout:
                    draw_expand_panel(self, context, layout, panel_name, props)

        elif props.tabs_menu == "FILE_RENDER":
            row = layout.row(align=True)
            draw_panel(self, context, row, "Collection Export", props)

        elif props.tabs_menu == "SETTING":
            # Object Info Settings
            box = layout.box()
            col = box.column(align=True)
            col.label(text="Setting")
            box = col.box()
            col = box.column(heading="Object Management:", align=True)
            row = col.row( align=True)
            row.prop(props, "uvmaps")
            row = col.row(align=True)
            row.prop(props, "custom_props")
            row = col.row(align=True)
            row.prop(props, "filter_props", text="Fillter")

            row = layout.row()
            draw_panel(self, context, row, "Keymap", props)

            if expand_panel_layout:
                for panel_name in expand_panel_layout:
                    draw_expand_panel(self, context, layout, panel_name, props)

            row = layout.row()
            row.template_icon(iconLib("duckx_symbol_type_frame_bg"), scale=5)

        
    
    

    
class DuckXMenu(Menu):
    bl_idname = "OBJECT_MT_duckx_tools"
    bl_label = "DuckX Tools"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'  # เพิ่มบรรทัดนี้
        if not context.area.type == 'IMAGE_EDITOR':
            if bpy.context.scene.tool_settings.use_transform_correct_face_attributes == True:
                layout.operator("duckx_tools.correct_face_attributes", text="Correct Face", icon="CHECKBOX_HLT")
            else:
                layout.operator("duckx_tools.correct_face_attributes", text="Correct Face", icon="CHECKBOX_DEHLT")
            layout.operator("duckx_tools.orienglobal", text="Orientation Global", icon="OBJECT_ORIGIN")
            
            if context.mode == 'EDIT_MESH':
                layout.operator("duckx_tools.orienselect", text="Orientation Select", icon="TRACKER")
                layout.operator("duckx_tools.scale_zero", text="A Scale 0", icon="DECORATE")
                layout.operator("duckx_tools.orien_and_pivot", text="Edge Pivot Align", icon="SNAP_MIDPOINT")
                layout.operator("duckx_tools.boundary_tools", text="Boundary Sharp", icon="MATPLANE")
                layout.operator("duckx_tools.delete_loose_parts", text="Delete Loose Part", icon="PANEL_CLOSE")
                layout.operator_menu_enum("duckx_tools.remove_loop_ring", property="action", text="Remove Ring Loop", icon="PANEL_CLOSE")
                layout.operator("duckx_tools.move_vert_to_activer", text="Move Vx At Last", icon="ARROW_LEFTRIGHT")
                layout.separator()
                layout.label(text="Merge by size")
                try:
                    layout.operator("duckx_tools.merge_by_size", text="Face", icon="LIGHTPROBE_PLANAR").action = "face"
                except:
                    layout.operator("duckx_tools.merge_by_size", text="Face", icon="LIGHTPROBE_PLANE").action = "face"
                layout.operator("duckx_tools.merge_by_size", text="Edge", icon="SNAP_MIDPOINT").action = "edge"
                layout.separator()
                layout.operator("duckx_tools.edge_length", text="Edge Length", icon="FIXED_SIZE")
            elif context.mode == 'OBJECT':
                layout.separator()
                layout.operator("duckx_tools.distance_calculator", text="Distance", icon=bl_icons("DRIVER_DISTANCE"))
            layout.separator()
            layout.operator_menu_enum("duckx_tools.object_wire", property="action", text="Wirew", icon="MESH_ICOSPHERE")
        else:
            layout.operator("duckx_tools.scale_zero", text="A Scale Zero", icon="DECORATE")
            #layout.operator("duckx_tools.uvpadding", text="+ " + "Padding", icon="MOD_EXPLODE").action = "more"
            #layout.operator("duckx_tools.uvpadding", text="- " + "Padding", icon="MOD_EXPLODE").action = "less"
            #layout.operator("duckx_tools.uv_unwarp_here", text="Unwarp Here", icon="UV")
            layout.operator("duckx_tools.uv_rotation", text="Q -90°").angle = -90
            layout.operator("duckx_tools.uv_rotation", text="E +90°").angle = 90
                
        #Console
        layout.separator()
        layout.operator("duckx_tools.console_command", text="Console", icon="CONSOLE")




class DUCKX_OT_ExpandPanel(bpy.types.Operator):
    bl_idname = "duckx_tools.duckx_expand_panel"
    bl_label = "Toggle Console Box"
    bl_description = "Expand/hide the panel"
    
    panel_name: StringProperty(name="Panel Name") # เพิ่ม property นี้

    def execute(self, context):
        if self.panel_name in expand_panel_layout:
            expand_panel_layout[self.panel_name]["expand"] = not expand_panel_layout[self.panel_name]["expand"]
            #print(f"Panel {self.panel_name} expanded: {expand_panel_layout[self.panel_name]['expand']}")
        return {'FINISHED'}

classes = [VIEW3D_PT_Duckx_MainPanel,DuckXMenu, DUCKX_OT_ExpandPanel]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


