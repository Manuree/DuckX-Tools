import bpy
from bpy.types import (Operator)
from bpy.props import (EnumProperty, PointerProperty, StringProperty, FloatVectorProperty, FloatProperty, IntProperty, BoolProperty)
from bpy.types import Panel

from ..icon_reg import *
from . import func_core
import math


edit_tab_name = False
dummy_data = [["collection", ["A", "B", "C"]], ["object", ["D", "E", "F"]]]

_cols = []

def enum_cols_callback(self, context):
    items = []
    for i, col in enumerate(_cols):
        items.append((col.name, col.name, "", i))
    return items


  
# ---------------------
# Helpers
# ---------------------
def add_tab(scene, name="Tab"):
    tab = scene.duckx_tools.tabs.add()
    tab.name = name
    scene.duckx_tools.tab_index = len(scene.duckx_tools.tabs)-1
    return tab

def add_group(tab, kind="OBJECTS", context=None):
    ctx = context or bpy.context

    grp = tab.groups.add()
    grp.kind = kind
    tab.group_index = len(tab.groups) - 1

    if kind == "OBJECTS":
        # ใช้เฉพาะ selection จริง ๆ (ไม่ fallback เป็น active)
        sel_objs = list(ctx.selected_objects) if ctx.selected_objects else []
        if not sel_objs:
            grp.name = "Objects Group"
            return grp

        # ตั้งชื่อ
        grp.name = sel_objs[0].name if len(sel_objs) == 1 else ", ".join(o.name for o in sel_objs)

        # เพิ่มรายการ
        for obj in sel_objs:
            if obj and all(it.obj != obj for it in grp.objects):
                it = grp.objects.add()
                it.obj = obj

        return grp

    elif kind == "COLLECTIONS":
        # ใช้ฟังก์ชันของคุณเท่านั้น
        cols = func_core.collections_from_selected_objects(ctx) or []

        # เก็บเฉพาะที่ไม่ซ้ำโดยดูจากชื่อ (คงลำดับ)
        seen = set()
        uniq_cols = []
        for c in cols:
            if c and c.name not in seen:
                seen.add(c.name)
                uniq_cols.append(c)

        if not uniq_cols:
            grp.name = "Collections Group"
            return grp

        # ตั้งชื่อ
        grp.name = uniq_cols[0].name if len(uniq_cols) == 1 else ", ".join(c.name for c in uniq_cols)

        # เพิ่มรายการ
        for c in uniq_cols:
            if all(it.col != c for it in grp.collections):
                it = grp.collections.add()
                it.col = c

        return grp

    return grp

def add_object(grp, obj):
    if grp.kind != "OBJECTS" or obj is None: return
    # กันซ้ำแบบง่าย
    if any(it.obj == obj for it in grp.objects): return
    it = grp.objects.add()
    it.obj = obj
    grp.obj_index = len(grp.objects)-1

def add_collection(grp, col):
    if grp.kind != "COLLECTIONS" or col is None: return
    if any(it.col == col for it in grp.collections): return
    it = grp.collections.add()
    it.col = col
    grp.col_index = len(grp.collections)-1

def remove_active_tab(scene):
    i = scene.duckx_tools.tab_index
    if 0 <= i < len(scene.duckx_tools.tabs):
        scene.duckx_tools.tabs.remove(i)
        scene.duckx_tools.tab_index = min(i, len(scene.duckx_tools.tabs)-1)

def remove_active_group(tab):
    i = tab.group_index
    if 0 <= i < len(tab.groups):
        tab.groups.remove(i)
        tab.group_index = min(i, len(tab.groups)-1)

class Duckx_OT_GroupTools(Operator):
    bl_idname = "duckx_tools.group_tools"
    bl_label = "Group Tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Show and Hide group objects"

    action : StringProperty(name="Action")
    tab_index : IntProperty(name="Tab Index")
    index : IntProperty(name="Index")
    hide_all = True
    invert = False
    select = False
    move = False
    
    
    
    def invoke(self, context, event):
        if event.shift:
            if event.ctrl:
                self.select = True
            self.hide_all = False
            return self.execute(context)
        elif event.ctrl and event.alt:
            self.move = True
            return self.execute(context)
        elif event.alt:
            self.invert = True
            return self.execute(context)
        elif event.ctrl:
            self.select = True
            return self.execute(context)
        else:
            return self.execute(context)
    
    def draw(self, context):
        layout = self.layout
    
    def execute(self, context):
        scene = context.scene
        prop = scene.duckx_tools

        
        
        
        return {'FINISHED'}
    
class Duckx_OT_GroupToolsAddTab(Operator):
    bl_idname = "duckx_tools.group_tools_add_tab"
    bl_label = "Add Tab"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene = context.scene
        prop = scene.duckx_tools

        
        add_tab(scene, "Untitled")
        
        return {'FINISHED'}
    
class Duckx_OT_GroupToolsRemovTab(Operator):
    bl_idname = "duckx_tools.group_tools_remove_tab"
    bl_label = "Remove Tab"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene = context.scene
        prop = scene.duckx_tools

        remove_active_tab(scene)
        
        return {'FINISHED'}
    
class Duckx_OT_GroupToolsActiveTab(Operator):
    bl_idname = "duckx_tools.group_tools_active_tab"
    bl_label = "Active Tab"
    bl_options = {"REGISTER"}  # เปลี่ยนชื่อ/สลับแท็บ ไม่จำเป็นต้อง UNDO
    bl_description = "[SHIFT CLICK] for Renname this tab"

    tab_index: bpy.props.IntProperty()
    # ใช้เฉพาะตอน rename
    rename_mode: bpy.props.BoolProperty(default=False, options={'SKIP_SAVE'})
    new_name: bpy.props.StringProperty(name="Tab name", default="")

    @classmethod
    def poll(cls, context):
        return context and context.scene and hasattr(context.scene, "duckx_tools")

    def invoke(self, context, event):
        scene = context.scene
        prop = scene.duckx_tools

        # safety
        if not hasattr(prop, "tabs") or len(prop.tabs) == 0:
            self.report({'WARNING'}, "No tabs available.")
            return {'CANCELLED'}
        if not (0 <= self.tab_index < len(prop.tabs)):
            self.report({'WARNING'}, f"Invalid tab index: {self.tab_index}")
            return {'CANCELLED'}

        if event.shift:
            # --- Rename mode ---
            self.rename_mode = True
            self.new_name = prop.tabs[self.tab_index].name  # preload ชื่อเดิม
            return context.window_manager.invoke_props_dialog(self, width=260)
        else:
            # --- Activate tab normally ---
            return self._activate_tab(context)

    def draw(self, context):
        if self.rename_mode:
            col = self.layout.column()
            col.label(text="Rename Tab")
            col.prop(self, "new_name", text="")

    def execute(self, context):
        # execute ถูกเรียกทั้งจาก invoke_props_dialog (rename) และจาก invoke แบบธรรมดา
        if self.rename_mode:
            return self._rename_tab(context)
        else:
            return self._activate_tab(context)

    # ---------------- helpers ----------------
    def _activate_tab(self, context):
        prop = context.scene.duckx_tools
        if 0 <= self.tab_index < len(prop.tabs):
            prop.tab_index = self.tab_index
            self._redraw(context)
            return {'FINISHED'}
        self.report({'WARNING'}, f"Invalid tab index: {self.tab_index}")
        return {'CANCELLED'}

    def _rename_tab(self, context):
        prop = context.scene.duckx_tools
        tab = prop.tabs[self.tab_index]

        # กันชื่อว่าง และตัด space ปลาย
        name = self.new_name.strip()
        if not name:
            self.report({'WARNING'}, "Name cannot be empty.")
            return {'CANCELLED'}

        tab.name = name
        # ตั้ง active ไว้ที่แท็บที่เพิ่งแก้ชื่อ (เผื่ออยากให้ชัด)
        prop.tab_index = self.tab_index

        self.report({'INFO'}, f"Renamed to: {name}")
        self._redraw(context)
        return {'FINISHED'}

    def _redraw(self, context):
        # ให้ทุกพื้นที่วาดใหม่ทันที
        for area in context.window.screen.areas:
            area.tag_redraw()

class Duckx_OT_GroupToolsAddGroup(Operator):
    bl_idname = "duckx_tools.group_tools_add_group"
    bl_label = "Add Group"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add selected item to group"

    @classmethod
    def poll(cls, context):
        if not (context and context.scene and hasattr(context.scene, "duckx_tools")):
            return False
        prop = context.scene.duckx_tools
        return hasattr(prop, "tabs") and len(prop.tabs) > 0 and 0 <= getattr(prop, "tab_index", -1) < len(prop.tabs)

    kind : EnumProperty(name="Kind", items=[
        ('COLLECTIONS', "Collections", "Add Collections to group"),
        ('OBJECTS', "Objects", "Add Objects to group"),
    ])

    def execute(self, context):
        scene = context.scene
        prop = scene.duckx_tools
        tab = prop.tabs[prop.tab_index]

        print(self.kind)
        add_group(tab, kind=self.kind)
        
        return {'FINISHED'}
    
class Duckx_OT_GroupToolsRemoveGroup(Operator):
    bl_idname = "duckx_tools.group_tools_remove_group"
    bl_label = "Remove Group"
    bl_options = {"REGISTER", "UNDO"}

    # ถ้าไม่ตั้งค่า จะใช้ active group's index ของแท็บปัจจุบันแทน
    group_index: bpy.props.IntProperty(default=-1)

    @classmethod
    def poll(cls, context):
        return context and context.scene and hasattr(context.scene, "duckx_tools")

    def execute(self, context):
        prop = context.scene.duckx_tools

        # มีแท็บไหม
        if not hasattr(prop, "tabs") or len(prop.tabs) == 0:
            self.report({'WARNING'}, "No tabs to remove from.")
            return {'CANCELLED'}

        # แท็บที่ active ตอนนี้
        t_idx = getattr(prop, "tab_index", -1)
        if not (0 <= t_idx < len(prop.tabs)):
            self.report({'WARNING'}, "No active tab.")
            return {'CANCELLED'}

        tab = prop.tabs[t_idx]
        groups = tab.groups

        if len(groups) == 0:
            self.report({'WARNING'}, "No groups to remove.")
            return {'CANCELLED'}

        # เลือก index ที่จะลบ: ถ้าไม่ได้ส่งมา ใช้ active group's index
        g_idx = self.group_index if self.group_index >= 0 else getattr(tab, "group_index", -1)
        if not (0 <= g_idx < len(groups)):
            self.report({'WARNING'}, f"Invalid group index: {g_idx}")
            return {'CANCELLED'}

        # ลบ
        groups.remove(g_idx)

        # จัดการ active index หลังลบ
        if len(groups) == 0:
            tab.group_index = -1
        else:
            tab.group_index = min(g_idx, len(groups) - 1)

        # redraw UI
        for area in context.window.screen.areas:
            area.tag_redraw()

        self.report({'INFO'}, "Group removed.")
        return {'FINISHED'}

class Duckx_OT_GroupToolsActiveGroup(Operator):
    bl_idname = "duckx_tools.group_tools_active_group"
    bl_label = "Active Group"
    bl_options = {"UNDO"}
    bl_description = "Show and Hide group objects \n[SHIFT CLICK] for ignore hide current \n[SHIFT + ALT] for show others and hide this group \n[CTRL] for select all in collection \n[ALT] for hide all in collection \n[CTRL + ALT] for move selected objects to this collection"

    group_index: bpy.props.IntProperty(default=-1)

    hide_others = True
    invert = False
    hide_invert = False
    select = False
    move = False

    @classmethod
    def poll(cls, context):
        return (context and context.scene and hasattr(context.scene, "duckx_tools")
                and hasattr(context.scene.duckx_tools, "tabs"))
    
    def invoke(self, context, event):
        if event.shift and event.alt:
            self.hide_invert = True
            return self.execute(context)
        elif event.shift:
            if event.ctrl:
                self.select = True
            self.hide_others = False
            return self.execute(context)
        elif event.ctrl and event.alt:
            self.move = True
            return self.execute(context)
        elif event.alt:
            self.invert = True
            return self.execute(context)
        elif event.ctrl:
            self.select = True
            return self.execute(context)
        else:
            return self.execute(context)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Group Tools")

    def execute(self, context):
        scene = context.scene
        prop = scene.duckx_tools
        t_idx = prop.tab_index

        if not (0 <= t_idx < len(prop.tabs)):
            self.report({'WARNING'}, "No active tab.")
            return {'CANCELLED'}

        tab = prop.tabs[t_idx]
        g_idx = self.group_index if self.group_index >= 0 else getattr(tab, "group_index", -1)

        if not (0 <= g_idx < len(tab.groups)):
            self.report({'WARNING'}, "No active group.")
            return {'CANCELLED'}

        group = tab.groups[g_idx]

        if group.kind == "OBJECTS":
            objs = []
            for it in group.objects:
                if it.obj:
                    objs.append(it.obj.name)

            if self.hide_invert:
                self.show_others_objects(context, objs)
            else:
                # Show Objects
                if self.invert == False:
                    self.show_objects(context, objs)
                else:
                    self.hide_objects(context, objs)

            print("------------------------------------------------------------------------")
            print(f"[Active Group: {group.name}] \nList:", objs)
            print("------------------------------------------------------------------------")
        else:  # COLLECTIONS
            cols = []
            for it in group.collections:
                if it.col:
                    cols.append(it.col)


            if self.hide_invert:
                self.show_others_collections(context, cols)
            else:
                # Show Collection
                if self.move == False:
                    if self.invert == False:
                        self.show_collections(context, cols)
                    else:
                        self.hide_collection(context, cols)
                else:
                    if len(cols) > 1:
                        global _cols
                        _cols = cols
                        bpy.ops.duckx_tools.group_tools_move_to_collections('INVOKE_DEFAULT')
                    else:
                        func_core.move_to_collection(cols[0])
            
            print("------------------------------------------------------------------------")
            print(f"[Active Group: {group.name}] \nList:", cols)
            print("------------------------------------------------------------------------")


        return {'FINISHED'}

    def show_others_objects(self, context, objects):
        print("Showing other collections...")
        # 1. Show ทุก Collections และ Objects
        for col in bpy.data.collections:
            print("Showing collection:", col.name)
            func_core.hide_collection(col.name, hide_viewport=False)
            for obj in col.objects:
                obj.hide_set(False)     # แสดง Object กลับมาใน Viewport

        # 2. ซ่อน Collection ที่อยู่ใน collections[]
        for obj in objects:
            if isinstance(obj, str):  # ถ้า collections[] ส่งมาเป็นชื่อ
                obj = bpy.data.objects.get(obj)
            if obj:  # ป้องกัน error ถ้าไม่เจอ
                obj.hide_set(True)
        return {'FINISHED'}
    
    def show_others_collections(self, context, collections):
        print("Showing other collections...")
        # 1. Show ทุก Collections และ Objects
        for col in bpy.data.collections:
            print("Showing collection:", col.name)
            func_core.hide_collection(col.name, hide_viewport=False)
            for obj in col.objects:
                obj.hide_set(False)     # แสดง Object กลับมาใน Viewport

        # 2. ซ่อน Collection ที่อยู่ใน collections[]
        for col in collections:
            if isinstance(col, str):  # ถ้า collections[] ส่งมาเป็นชื่อ
                col = bpy.data.collections.get(col)
            if col:  # ป้องกัน error ถ้าไม่เจอ
                func_core.hide_collection(col.name, hide_viewport=True)
                for obj in col.objects:
                    obj.hide_set(True)
        return {'FINISHED'}

    def hide_objects(self, context, objects):
        if not objects:
            return {'CANCELLED'}

        # ทำให้เป็น list ของ bpy.types.Object
        objs = []
        for o in objects:
            if isinstance(o, bpy.types.Object):
                objs.append(o)
            elif isinstance(o, str):
                ob = bpy.data.objects.get(o)
                if ob:
                    objs.append(ob)

        if not objs:
            return {'CANCELLED'}

        for ob in objs:
            try:
                ob.hide_set(True)  # ซ่อนใน Viewport
            except Exception:
                pass
            #ob.hide_viewport = True  # กันพลาดถ้า hide_set ไม่รองรับ

        return {'FINISHED'}
        
    def hide_collection(self, context, collections):
        # ทำให้ collections เป็น list ของชื่อ
        col_names = []
        if not collections:
            return {'CANCELLED'}

        for c in collections:
            if isinstance(c, bpy.types.Collection):
                col_names.append(c.name)
            elif isinstance(c, str):
                col_names.append(c)
            else:
                # กันกรณีส่ง type แปลก ๆ มา
                continue

        # สร้างฟังก์ชันค้นหา LayerCollection ใน View Layer ปัจจุบัน
        def find_layer_collection(layer_coll, name):
            if layer_coll.collection.name == name:
                return layer_coll
            for child in layer_coll.children:
                found = find_layer_collection(child, name)
                if found:
                    return found
            return None

        # วนซ่อนทีละคอลเลกชัน
        for name in col_names:
            lc = find_layer_collection(context.view_layer.layer_collection, name)
            if lc:
                lc.hide_viewport = True

        return {'FINISHED'}
    
    def show_objects(self, context, objects):
        # กลับสู่ OBJECT mode
        try:
            bpy.ops.object.mode_set(mode='OBJECT')
        except Exception:
            pass

        # ทำให้เป็นลิสต์ของ Object จริง ๆ
        targets = []
        for ob in (objects or []):
            if isinstance(ob, bpy.types.Object):
                targets.append(ob)
            elif isinstance(ob, str):
                o = bpy.data.objects.get(ob)
                if o:
                    targets.append(o)

        if not targets:
            return {'FINISHED'}

        # ------- เปิดเฉพาะคอลเลกชันที่จำเป็นสำหรับเป้าหมาย -------
        keep_names = set()
        for ob in targets:
            for c in getattr(ob, "users_collection", []) or []:
                # รวมทั้งสายพ่อ/ลูกของคอลเลกชันนั้น
                for nm in func_core.get_hierarchy_collections(c):
                    if nm:
                        keep_names.add(nm)

        if getattr(self, "hide_others", False):
            # ซ่อนคอลเลกชันอื่นทั้งหมด
            for coll in bpy.data.collections:
                func_core.hide_collection(coll.name, hide_viewport=(coll.name not in keep_names))
        else:
            # แค่ unhide ที่จำเป็น
            for nm in keep_names:
                func_core.hide_collection(nm, hide_viewport=False)

        # ------- โชว์เฉพาะวัตถุเป้าหมาย และซ่อนวัตถุอื่น (สำคัญ!) -------
        target_set = set(targets)

        # โชว์เป้าหมาย
        for ob in target_set:
            try:
                ob.hide_set(False)
            except Exception:
                pass
            #ob.hide_viewport = False

        # ถ้าให้ซ่อนตัวอื่นด้วย ให้ซ่อนทุกตัวที่ไม่ใช่เป้าหมาย
        if getattr(self, "hide_others", False):
            for ob in bpy.data.objects:
                if ob not in target_set:
                    try:
                        ob.hide_set(True)
                    except Exception:
                        pass
                    #ob.hide_viewport = True

        # เลือกและตั้ง active ให้เป้าหมายตัวแรก (ถ้าต้องการ)
        try:
            bpy.ops.object.select_all(action='DESELECT')
        except Exception:
            pass
        for ob in targets:
            ob.select_set(True)
        context.view_layer.objects.active = targets[0]

        return {'FINISHED'}
    
    def show_collections(self, context, collections):
        # 1) กลับสู่ OBJECT mode และเคลียร์ selection ด้วย operator เพียงครั้งเดียว
        with context.temp_override():
            try:
                bpy.ops.object.mode_set(mode='OBJECT')
            except Exception:
                pass
            try:
                bpy.ops.object.select_all(action='DESELECT')
            except Exception:
                pass

        # 2) ทำรายชื่อเป้าหมาย (ชื่อคอลเลกชัน)
        target_names = []
        if collections:
            for c in collections:
                name = c.name if isinstance(c, bpy.types.Collection) else str(c)
                if name and name not in target_names:
                    target_names.append(name)
        if not target_names:
            return {'FINISHED'}

        # 3) รวมเครือญาติคอลเลกชันทั้งหมดด้วยชื่อ (parent/child) โดยไม่ไปยุ่ง selection ตรงนี้
        keep_names = set()
        for name in target_names:
            col = bpy.data.collections.get(name)
            if not col:
                continue
            for nm in func_core.get_hierarchy_collections(col):
                if nm:
                    keep_names.add(nm)
            keep_names.add(name)
        keep_names.discard(None)
        if not keep_names:
            return {'FINISHED'}

        # 4) ซ่อน/โชว์คอลเลกชันให้เรียบร้อย “ก่อน” แล้วค่อยยุ่งกับออบเจ็กต์
        if getattr(self, "hide_others", False):
            for coll in bpy.data.collections:
                func_core.hide_collection(coll.name, hide_viewport=(coll.name not in keep_names))
        else:
            for nm in keep_names:
                func_core.hide_collection(nm, hide_viewport=False)

        # 5) เก็บ “รายการออบเจ็กต์ที่จะโชว์และเลือก” ให้ครบก่อน (หลีกเลี่ยงใช้ all_objects ระหว่างเพิ่งเปลี่ยน visibility)
        to_show = []
        for name in target_names:
            col = bpy.data.collections.get(name)
            if not col:
                continue
            # ใช้ col.objects โดยตรงเพื่อลด side effect; ถ้าต้องการลูก ๆ ให้เดินซ้ำเอง
            stack = [col]
            seen_cols = set()
            while stack:
                cc = stack.pop()
                if cc in seen_cols:
                    continue
                seen_cols.add(cc)
                for ob in cc.objects:
                    if ob not in to_show:
                        to_show.append(ob)
                for ch in cc.children:
                    stack.append(ch)
        
        # >>> NEW: ซ่อนอ็อบเจ็กต์ที่ไม่อยู่ในคอลเลกชันเป้าหมาย (แก้เคสที่อยู่ใน Scene Collection/Master)
        if getattr(self, "hide_others", False):
            allowed = set(to_show)  # อ็อบเจ็กต์ที่ต้องการให้โชว์ (เฉพาะของคอลเลกชันเป้าหมาย)
            for ob in bpy.data.objects:
                if ob not in allowed:
                    try:
                        ob.hide_set(True)   # ซ่อนแบบเป็นรายอ็อบเจ็กต์
                    except Exception:
                        pass

        if not to_show:
            # ยังตั้ง active layer collection ให้ถูก แม้ไม่มีออบเจ็กต์
            self._set_active_layer_collection_by_name(context, target_names[0])
            return {'FINISHED'}

        # 6) unhide อ็อบเจ็กต์เป้าหมาย
        for ob in to_show:
            ob.hide_set(False)
            #ob.hide_viewport = False

        # 7) ตั้ง selection และ active object หลัง visibility stable แล้ว
        try:
            for ob in to_show:
                if ob.visible_get():
                    ob.select_set(True)
            context.view_layer.objects.active = next((o for o in to_show if o.visible_get()), to_show[0])
        except Exception:
            pass

        # 8) สุดท้าย ค่อยตั้ง active layer collection เป็นคอลเลกชันแรก
        self._set_active_layer_collection_by_name(context, target_names[0])
        return {'FINISHED'}

    # helper ภายในคลาสเดียวกัน (ลดการซ้ำโค้ดและหลบ crash)
    def _set_active_layer_collection_by_name(self, context, name: str):
        def find_layer_collection(lc, nm):
            if lc.collection and lc.collection.name == nm:
                return lc
            for ch in lc.children:
                f = find_layer_collection(ch, nm)
                if f:
                    return f
            return None
        lc = find_layer_collection(context.view_layer.layer_collection, name)
        if lc:
            context.view_layer.active_layer_collection = lc
    

class Duckx_OT_GroupToolsMoveToCollections(Operator):
    bl_idname = "duckx_tools.group_tools_move_to_collections"
    bl_label = "Move to Collections"
    bl_options = {"UNDO"}

    col_target: EnumProperty(
        name="Target Collection",
        description="Choose collection to move object",
        items=enum_cols_callback
    )

    def invoke(self, context, event):
        if not _cols:
            self.report({'WARNING'}, "No collections in _cols")
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.prop(self, "col_target", text="Collection", expand=True)

    def execute(self, context):
        target_col = bpy.data.collections.get(self.col_target)
        print(self.col_target)
        if not target_col:
            self.report({'WARNING'}, "Collection not found")
            return {'CANCELLED'}

        func_core.move_to_collection(target_col)

        return {'FINISHED'}
        
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
        prop = scene.duckx_tools 
        active_tab_index = prop.tab_index 

        layout = self.layout
        col = layout.column(align=True)
        row = col.row(align=True)
        row.alignment = "CENTER"

        # Draw tab
        for i, tab in enumerate(prop.tabs):
            is_active = (i == active_tab_index)
            op = row.operator("duckx_tools.group_tools_active_tab", text=tab.name, depress=is_active)
            op.tab_index = i  # ส่ง index ไปยัง operator

        row.operator("duckx_tools.group_tools_add_tab", text="", icon=bl_icons("ADD"))
        row.operator("duckx_tools.group_tools_remove_tab", text="", icon=bl_icons("REMOVE"))

        # Draw Group Box
        col = layout.column(align=True)
        box = col.box()
        col = box.column(align=True)
        if 0 <= active_tab_index < len(prop.tabs):
            tab = prop.tabs[active_tab_index]  # Tab ที่ Active อยู่
            for i, group in enumerate(tab.groups):
                row = col.row(align=True)

                if group.kind == "OBJECTS":
                    group_icon = bl_icons("OBJECT_DATA")
                else:  # "COLLECTIONS"
                    group_icon = bl_icons("OUTLINER_COLLECTION")

                # ต้องกำหนด group_index ให้ operator ทุกครั้งในลูป
                op = row.operator("duckx_tools.group_tools_active_group", text=(group.name or "-"), icon=group_icon)
                op.group_index = i  # <<< สำคัญ
                row.operator("duckx_tools.group_tools_remove_group", text="", icon=bl_icons("TRASH")).group_index = i
        row = box.row()
        row.alignment = "CENTER"
        row.operator("duckx_tools.group_tools_add_group", text="+", icon=bl_icons("OUTLINER_COLLECTION")).kind = "COLLECTIONS"
        row.operator("duckx_tools.group_tools_add_group", text="+", icon=bl_icons("OBJECT_DATA")).kind = "OBJECTS"
        #row.operator("duckx_tools.group_tools_remove_group", text="", icon=bl_icons("REMOVE"))


def register():
    bpy.utils.register_class(Duckx_OT_GroupTools)
    bpy.utils.register_class(Duckx_OT_GroupToolsAddTab)
    bpy.utils.register_class(Duckx_OT_GroupToolsRemovTab)
    bpy.utils.register_class(Duckx_OT_GroupToolsActiveTab)
    bpy.utils.register_class(Duckx_OT_GroupToolsAddGroup)
    bpy.utils.register_class(Duckx_OT_GroupToolsRemoveGroup)
    bpy.utils.register_class(Duckx_OT_GroupToolsActiveGroup)
    bpy.utils.register_class(Duckx_OT_GroupToolsMoveToCollections)

    bpy.utils.register_class(VIEW3D_PT_Duckx_Groups)

        
    
def unregister():
    bpy.utils.unregister_class(Duckx_OT_GroupTools)
    bpy.utils.unregister_class(Duckx_OT_GroupToolsAddTab)
    bpy.utils.unregister_class(Duckx_OT_GroupToolsRemovTab)
    bpy.utils.unregister_class(Duckx_OT_GroupToolsActiveTab)
    bpy.utils.unregister_class(Duckx_OT_GroupToolsAddGroup)
    bpy.utils.unregister_class(Duckx_OT_GroupToolsRemoveGroup)
    bpy.utils.unregister_class(Duckx_OT_GroupToolsActiveGroup)
    bpy.utils.unregister_class(Duckx_OT_GroupToolsMoveToCollections)

    bpy.utils.unregister_class(VIEW3D_PT_Duckx_Groups)

