import bpy


from contextlib import suppress




def collections_from_selected_objects(context):
    """อ่านคอลเลคชันที่ถูกเลือกใน Outliner (รองรับ VIEW_LAYER)"""
    found = []
    """อ่านคอลเลคชันที่ถูกเลือกใน Outliner (รองรับ VIEW_LAYER) — แบบทนทานต่อเวอร์ชัน"""
    found = []

    def add_coll(c):
        if c and isinstance(c, bpy.types.Collection) and c not in found:
            found.append(c)

    wm = getattr(context, "window_manager", None)
    if not wm:
        wm = bpy.context.window_manager if hasattr(bpy.context, "window_manager") else None

    if wm:
        for win in wm.windows:
            scr = getattr(win, "screen", None)
            if not scr:
                continue
            for area in getattr(scr, "areas", []):
                if getattr(area, "type", None) != 'OUTLINER':
                    continue

                regions = getattr(area, "regions", None) or []
                for region in regions:
                    if getattr(region, "type", None) != 'WINDOW':
                        continue

                    # บางรุ่น temp_override จะ throw ถ้า args ไม่ครบ/ไม่รองรับ
                    with suppress(Exception):
                        with context.temp_override(window=win, area=area, region=region):
                            sel = getattr(context, "selected_ids", []) or []
                            if not sel:
                                continue
                            for it in sel:
                                if isinstance(it, bpy.types.Collection):
                                    add_coll(it)
                                elif isinstance(getattr(it, "collection", None), bpy.types.Collection):
                                    add_coll(it.collection)
                                elif isinstance(it, bpy.types.Object):
                                    for c in getattr(it, "users_collection", []) or []:
                                        add_coll(c)

    # fallback: ถ้าไม่เจออะไรเลย ใช้ active layer collection
    if not found:
        vl = getattr(context, "view_layer", None)
        alc = getattr(vl, "active_layer_collection", None) if vl else None
        if alc and isinstance(getattr(alc, "collection", None), bpy.types.Collection):
            add_coll(alc.collection)

    return found

def hide_collection(collection_name:str, hide_viewport:bool = True):
    # ค้นหา LayerCollection ใน View Layer ปัจจุบัน
    layer_collections = bpy.context.view_layer.layer_collection

    # ฟังก์ชันค้นหา LayerCollection ตามชื่อ
    def find_layer_collection(layer_collection, name):
        if layer_collection.name == name:
            return layer_collection
        for child in layer_collection.children:
            found = find_layer_collection(child, name)
            if found:
                return found
        return None

    # ค้นหาคอลเลคชันที่ต้องการ
    target_layer_collection = find_layer_collection(layer_collections, collection_name)

    if target_layer_collection:
        # พับคอลเลคชัน
        target_layer_collection.hide_viewport = hide_viewport
        print(f"Collapsed collection '{collection_name}'")
    else:
        print(f"Collection '{collection_name}' not found")


def select_objects_in_collection(collection_name):
    # ตรวจสอบว่ามีคอลเลคชันชื่อนั้นหรือไม่
    collection = bpy.data.collections.get(collection_name)
    if collection:
        # ยกเลิกการเลือกวัตถุทั้งหมดก่อน
        bpy.ops.object.select_all(action='DESELECT')

        # เลือกวัตถุทั้งหมดในคอลเลคชันนั้น
        for obj in collection.objects:
            obj.select_set(True)
        
        # ตั้งวัตถุที่เลือกอันแรกเป็น active
        if collection.objects:
            bpy.context.view_layer.objects.active = collection.objects[0]
        
        print(f"Selected all objects in collection '{collection_name}'")
    else:
        print(f"Collection '{collection_name}' not found")

def get_hierarchy_collections(collection):
    collections_list = []

    # Traverse upward to get all parents
    def find_parent(collection):
        for coll in bpy.data.collections:
            if collection.name in coll.children:
                return coll
        return None

    # Traverse downward to get all children
    def traverse_children(collection):
        collections_list.append(collection.name)
        for child in collection.children:
            traverse_children(child)

    # Add the collection itself
    collections_list.append(collection.name)

    # Traverse up to parent collections
    parent = find_parent(collection)
    while parent:
        collections_list.append(parent.name)
        parent = find_parent(parent)

    # Traverse down to child collections
    traverse_children(collection)

    # Remove duplicates (in case a collection is both parent and child)
    collections_list = list(set(collections_list))

    return collections_list

def collection_color_icon(coll: bpy.types.Collection) -> str:
    tag = getattr(coll, "color_tag", "NONE")
    mapping = {
        "NONE":     "OUTLINER_COLLECTION",
        "COLOR_01": "COLLECTION_COLOR_01",
        "COLOR_02": "COLLECTION_COLOR_02",
        "COLOR_03": "COLLECTION_COLOR_03",
        "COLOR_04": "COLLECTION_COLOR_04",
        "COLOR_05": "COLLECTION_COLOR_05",
        "COLOR_06": "COLLECTION_COLOR_06",
        "COLOR_07": "COLLECTION_COLOR_07",
        "COLOR_08": "COLLECTION_COLOR_08",
    }
    return mapping.get(tag, "OUTLINER_COLLECTION")