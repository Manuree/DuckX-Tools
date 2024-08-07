import bpy
import bmesh

import urllib.request
import zipfile
import os
import subprocess
import json
import textwrap
from math import radians, cos, sin, degrees, atan2, pi
from mathutils import Matrix, Vector


def get_triangle():
    selected_objects = bpy.context.selected_objects
    num_triangles = 0
    if selected_objects is not None:
        for obj in selected_objects:
            if obj.type == 'MESH':
                mesh = obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
                num_triangles += sum(len(p.vertices) - 2 for p in mesh.polygons)
        return(num_triangles)

def char_extend(text=""):
    characters = []
    for name in text:
        name_characters = list(name)
        characters.extend(name_characters)
    return characters

def suffix_separator(text="", separator=1):
    characters = char_extend(text)
    if characters:
        for i in range(separator):
            characters.pop()
    prefix =''.join(characters)
    return (prefix)

def find_word(text="", word="_LOD0"):
    _word = []
    matching = 0
    match = False
    if matching < len(word):
        for i in range(len(text)):
            if word[matching] == text[i]:
                matching += 1
                _word.append(text[i])
                if matching == len(word):
                    break
            else:
                _word = []
                matching = 0

    characters =''.join(_word)
    word = ''.join(word)
    if characters == word:
        match = True
    else:
        match = False
    return match

def TextWrap(context, text, parent, line_height):
    chars = int(context.region.width / 7)   # 7 pix on 1 character
    wrapper = textwrap.TextWrapper(width=chars)
    text_lines = wrapper.wrap(text=text)
    for text_line in text_lines:
        row = parent.row(align=True)
        row.label(text=text_line)
        row.scale_y = line_height

def word_check(text, key):
  if key in text:
    return True
  else:
    return False

def list_to_string(list):
    # Convert list to a JSON-formatted string
    try:
        string = json.dumps(list)
    except:
        string = ""
    return string

def string_to_list(string):
    # Convert the JSON-formatted string back to a list
    try:
        list = json.loads(string)
    except:
        list = []
    return list

def load_jsonFile(fileName, location):
    addon_directory = os.path.dirname(__file__)
    resources_directory = os.path.join(addon_directory, location)
    json_file_path = os.path.join(resources_directory, fileName + ".json")

    if os.path.exists(json_file_path):
        with open(json_file_path, "r") as file:
            data = json.load(file)
            file.close()
    else:
        print("JSON file not found.")
    return data

def read_txt_file(filename, location):
    patch_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), location)
    file_path = os.path.join(patch_dir, filename)
    try:
        with open(file_path, "r") as file:
            lines = file.read().splitlines()
            return lines
    except FileNotFoundError:
        print(f"File '{filename}' not found in the 'patch' folder.")
        return None
    except Exception as e:
        print(f"Error occurred while reading the file: {e}")
        return None

def message_box(message = "", title = "Message Box", icon = 'INFO'):
    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

def clipboard(value):
    try:
        # Convert the value to a string before copying
        value_str = str(value)

        # Use the appropriate command based on the operating system
        if subprocess.os.name == "nt":  # Windows
            subprocess.run(["clip"], input=value_str, text=True, check=True)
        else:  # Linux or macOS
            subprocess.run(["pbcopy"], input=value_str.encode("utf-8"), check=True)

        print("Value copied to clipboard successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

def edge_length():
    # Get the active object
    edgeslength = 0.0
    obj = bpy.context.active_object

    # Check if the active object exists and is a mesh
    if obj and obj.type == 'MESH':
        # Check if the object is in Edit Mode
        if obj.mode == 'EDIT':
            # Get the active mesh data
            mesh = obj.data

            # Create a BMesh from the mesh data
            bm = bmesh.from_edit_mesh(mesh)

            # Get the selected edges
            selected_edges = [edge for edge in bm.edges if edge.select]

            # Calculate and print the length of each selected edge
            for edge in selected_edges:
                v1 = obj.matrix_world @ edge.verts[0].co
                v2 = obj.matrix_world @ edge.verts[1].co
                edge_length = (v2 - v1).length
                edgeslength += edge_length

            # Update the BMesh back to the mesh data
            bmesh.update_edit_mesh(mesh)

            # Free the BMesh
            bm.free()
        else:
            print("Please enter Edit Mode to calculate edge lengths.")
    else:
        print("No active mesh object found.")
    #print("Edge length:", edge_length)
    return edgeslength

def get_all_object_names():
    # Get the objects in the current scene
    objects = bpy.context.scene.objects
    
    # Create an empty list to store the object names
    object_names = []
    
    # Iterate over the objects and append their names to the list
    for obj in objects:
        object_names.append(obj.name)
    
    return object_names

def get_collection_items(self, context):
    items = []
    collections = bpy.data.collections
    index = 1
    collecttionTag = "NONE"
    for collection in collections:
        if collection.color_tag != "NONE":
            collecttionTag = "COLLECTION_"+collection.color_tag
        else:
            collecttionTag = "OUTLINER_COLLECTION"
        items.append((collection.name, collection.name, "", collecttionTag, index))
        index +=1
    return items

def move_to_collection(collection_name):
    # Get or create the target collection
    collection = bpy.data.collections.get(collection_name)
    if not collection:
        collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(collection)

    # Move the selected objects to the collection
    selected_objects = bpy.context.selected_objects
    for obj in selected_objects:
        if obj.users_collection:
            obj.users_collection[0].objects.unlink(obj)
        collection.objects.link(obj)

def select_collection_by_name(collection_name):
    # Get the current scene
    scene = bpy.context.scene

    # Iterate over all collections in the scene
    for collection in scene.collection.children:
        if collection.name == collection_name:
            # Select the collection
            bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[collection.name]
            return True

    # If the collection was not found, return False
    return False

def focus_object_in_outliner():
    #pass
    try:
        for area in [a for a in bpy.context.screen.areas if a.type == 'OUTLINER']:
            for region in [r for r in area.regions if r.type == 'WINDOW']:
                override = {'area':area, 'region': region}
                bpy.ops.outliner.show_active(override)
    except:
        for area in [a for a in bpy.context.screen.areas if a.type == 'OUTLINER']:
            for region in [r for r in area.regions if r.type == 'WINDOW']:
                try:
                    with bpy.context.temp_override(area=area, region=region):
                        bpy.ops.outliner.show_active()
                except:
                    pass

def objects_to_list():
    items = []
    selected_objects = bpy.context.selected_objects
    for obj in selected_objects:
        items.append(obj.name)
    return items

def select_objects_by_name(name_list):
    try:
        for obj in bpy.context.scene.objects:
            if obj.name in name_list:
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
            else:
                obj.select_set(False)
    except:
        pass

def select_object_by_name(name):
    if name in bpy.data.objects:
        obj = bpy.data.objects[name]
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        return True
    else:
        return False

def deselect_objects_by_name(name_list):
    for obj in bpy.context.scene.objects:
        if obj.name in name_list:
            obj.select_set(False)
            

def deselect_object_by_name(name):
    obj = bpy.data.objects.get(name)
    if obj:
        obj.select_set(False)
        bpy.context.view_layer.objects.active = None


def select_face_by_size(size=""):
    # Get the active object in Edit Mode
    bpy.ops.object.mode_set(mode='EDIT')
    obj = bpy.context.active_object
    if obj and obj.type == 'MESH' and bpy.context.mode == 'EDIT_MESH':
        bpy.ops.mesh.select_all(action='DESELECT')
        bm = bmesh.from_edit_mesh(obj.data)
        
        # Find the face with the largest area
        a_face = None
        if size == "S":
            f_area = float('inf')
        elif size == "L":
            f_area = 0.0
        else:
            print("Intut S or L")
        for face in bm.faces:
            area = face.calc_area()
            if size == "S":
                if area < f_area:
                    f_area = area
                    a_face = face
            elif size == "L":
                if area > f_area:
                    f_area = area
                    a_face = face
        
        # Select the largest face
        if a_face:
            a_face.select_set(True)
        
        bmesh.update_edit_mesh(obj.data)
    #bpy.ops.object.mode_set(mode='OBJECT')

addon_version=""
def get_addon_version():
    # this is set in __init__
    return addon_version

dlProg = ""
extProg = ""
def update_addon(self, context, file_id, zip_filename):
    try:
        os.remove(zip_filename)
    except:
        print("No file update")
    try:
        UPDATED_ADDON_URL = url = f"https://drive.google.com/uc?id={file_id}"
        # Get the addon directory and the current addon file path
        addon_dir = os.path.dirname(os.path.realpath(__file__))
        addon_file = os.path.join(addon_dir, "__init__.py")
        # Download the updated addon zip file
        def download_progress(block_count, block_size, total_size):
            downloaded = block_count * block_size
            percent = int((downloaded / total_size) * 100)
            global dlProg
            dlProg = f"Downloaded: {percent}%"
            print(f"Downloaded: {percent}%")

        urllib.request.urlretrieve(UPDATED_ADDON_URL, filename=zip_filename, reporthook=download_progress)
  
        with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
            total_files = len(zip_ref.infolist())
            extracted_files = 0
            for file_info in zip_ref.infolist():
                zip_ref.extract(file_info, addon_dir)
                extracted_files += 1
                percent = int((extracted_files / total_files) * 100)
                global extProg
                extProg = f"Extracted: {percent}%"
                print(f"Extracted: {percent}%")

        # Remove the downloaded zip file
        os.remove(zip_filename)
        # Reload the addon module
        #bpy.ops.script.reload()
        self.report({'INFO'}, "Addon Updated. Please Restart Blender.")
    except:
        self.report({'INFO'}, "Addon Updater Error")

    
def update_patch(file_id, filename):
    try:
        UPDATED_ADDON_URL = url = f"https://drive.google.com/uc?id={file_id}"
        # Get the patch directory
        patch_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "patch")
        # Ensure the "patch" folder exists; if not, create it
        os.makedirs(patch_dir, exist_ok=True)
        # Download the updated addon file
        response = urllib.request.urlopen(UPDATED_ADDON_URL)
        data = response.read()
        # Save the updated addon file in the patch directory
        updated_addon_file = os.path.join(patch_dir, filename)
        with open(updated_addon_file, "wb") as f:
            f.write(data)

        print("Check Addon Updated.")
    except:
        print("Check Addon Updated Error")



def refresh_panel():
    for area in bpy.context.workspace.screens[0].areas:
                if area.type == 'VIEW_3D':
                    for region in area.regions:
                        if region.type == 'UI':
                            region.tag_redraw()
                            break


def blend_numbers(numA, numB, steps=3):
    if steps < 2:
        raise ValueError("Number of steps must be at least 2.")

    blended_values = [numA]
    step_size = (numB - numA) / (steps - 1)

    for i in range(1, steps - 1):
        next_value = numA + i * step_size
        blended_values.append(next_value)

    blended_values.append(numB)

    return blended_values


def compare_colors(color1, color2):
    # Define a tolerance for floating-point comparisons
    epsilon = 0.001

    # Compare each component of the color tuple
    for c1, c2 in zip(color1, color2):
        if abs(c1 - c2) > epsilon:
            return False

    return True

def get_active_uv_island_position():
    """
    Returns the average UV coordinates of the active UV island. 

    The active UV island is determined by the currently selected faces in Edit Mode.

    Returns:
        tuple: (avg_u, avg_v) - The average U and V coordinates of the island, 
               or (None, None) if no faces are selected or an error occurs.
    """

    obj = bpy.context.active_object
    if obj.type != 'MESH':
        return None, None

    if obj.mode != 'EDIT':
        return None, None

    me = obj.data
    bm = bmesh.from_edit_mesh(me)

    uv_layer = bm.loops.layers.uv.active
    if not uv_layer:
        return None, None

    selected_faces = [face for face in bm.faces if face.select]
    if not selected_faces:
        return None, None

    island = get_uv_island(bm, selected_faces[0], uv_layer)
    avg_u, avg_v = calculate_average_uv(island, uv_layer)

    return avg_u, avg_v

def move_selected_uv(delta_u=0.0, delta_v=0.0):
    """
    Moves the UV coordinates of selected faces by the given delta values.

    Args:
        delta_u (float): The amount to move the U coordinate.
        delta_v (float): The amount to move the V coordinate.
    """

    # Get the active object
    obj = bpy.context.active_object

    # Check if the object is a mesh
    if obj.type != 'MESH':
        return

    # Enter edit mode
    bpy.ops.object.mode_set(mode='EDIT')

    # Get the mesh data and bmesh representation
    me = obj.data
    bm = bmesh.from_edit_mesh(me)

    # Ensure UV layer is active
    uv_layer = bm.loops.layers.uv.verify()

    # Iterate over selected faces
    for face in bm.faces:
        if face.select:
            # Iterate over loops in the face
            for loop in face.loops:
                # Move the UV coordinates
                loop[uv_layer].uv.x += delta_u
                loop[uv_layer].uv.y += delta_v

    # Update the mesh data
    bmesh.update_edit_mesh(me)
    
def move_selected_uv_island(target_u=0.5, target_v=0.5):
    """
    Moves the UV island of selected faces to the target UV coordinates.

    Args:
        target_u (float): The target U coordinate for the island.
        target_v (float): The target V coordinate for the island.
    """

    # Get the active object and mesh data
    obj = bpy.context.active_object
    me = obj.data

    # Check if the object is a mesh
    if obj.type != 'MESH':
        return

    # Enter edit mode
    bpy.ops.object.mode_set(mode='EDIT')

    # Get the bmesh representation
    bm = bmesh.from_edit_mesh(me)

    # Ensure UV layer is active
    uv_layer = bm.loops.layers.uv.verify()

    # Find the selected UV island
    selected_faces = [face for face in bm.faces if face.select]
    if not selected_faces:
        return

    island = get_uv_island(bm, selected_faces[0], uv_layer)

    # Calculate the average UV coordinates of the island
    avg_u, avg_v = calculate_average_uv(island, uv_layer)

    # Calculate the translation vector
    delta_u = target_u - avg_u
    delta_v = target_v - avg_v

    # Move the island to the target location
    for face in island:
        for loop in face.loops:
            loop[uv_layer].uv.x += delta_u
            loop[uv_layer].uv.y += delta_v

    # Update the mesh data
    bmesh.update_edit_mesh(me)


def get_uv_island(bm, start_face, uv_layer):
    """
    Returns a list of faces belonging to the UV island of the given start face.

    Args:
        bm (bmesh.types.BMesh): The bmesh representation of the mesh.
        start_face (bmesh.types.BMFace): The face to start the island search from.
        uv_layer (bmesh.types.BMLayerItem): The active UV layer.

    Returns:
        list: A list of faces belonging to the UV island.
    """

    island = []
    visited = set()
    queue = [start_face]

    while queue:
        face = queue.pop(0)
        if face in visited:
            continue

        visited.add(face)
        island.append(face)

        for edge in face.edges:
            for other_face in edge.link_faces:
                if other_face != face and other_face not in visited:
                    is_connected = False
                    for loop1 in face.loops:
                        for loop2 in other_face.loops:
                            if loop1[uv_layer].uv == loop2[uv_layer].uv:
                                is_connected = True
                                break
                        if is_connected:
                            break
                    if is_connected:
                        queue.append(other_face)

    return island


def calculate_average_uv(faces, uv_layer):
    """
    Calculates the average UV coordinates of the given faces.

    Args:
        faces (list): A list of faces to calculate the average UV for.
        uv_layer (bmesh.types.BMLayerItem): The active UV layer.

    Returns:
        tuple: The average U and V coordinates.
    """

    total_u = 0.0
    total_v = 0.0
    count = 0

    for face in faces:
        for loop in face.loops:
            total_u += loop[uv_layer].uv.x
            total_v += loop[uv_layer].uv.y
            count += 1

    return total_u / count, total_v / count

def rotate_selected_uv_island(angle):
    """
    Rotates the UV island of selected faces around the island's center.

    Args:
        angle (float): The angle of rotation in degrees.
    """

    # Get the active object and mesh data
    obj = bpy.context.active_object
    me = obj.data

    # Check if the object is a mesh
    if obj.type != 'MESH':
        return

    # Enter edit mode
    bpy.ops.object.mode_set(mode='EDIT')

    # Get the bmesh representation
    bm = bmesh.from_edit_mesh(me)

    # Ensure UV layer is active
    uv_layer = bm.loops.layers.uv.verify()

    # Find the selected UV island
    selected_faces = [face for face in bm.faces if face.select]
    if not selected_faces:
        return

    island = get_uv_island(bm, selected_faces[0], uv_layer)

    # Calculate the center of the UV island
    pivot_u, pivot_v = calculate_average_uv(island, uv_layer)

    # Convert angle to radians
    angle = radians(angle)

    # Rotate the UVs in the island
    for face in island:
        for loop in face.loops:
            # Get the UV coordinates relative to the pivot
            u = loop[uv_layer].uv.x - pivot_u
            v = loop[uv_layer].uv.y - pivot_v

            # Apply the rotation
            rotated_u = u * cos(angle) - v * sin(angle)
            rotated_v = u * sin(angle) + v * cos(angle)

            # Update the UV coordinates
            loop[uv_layer].uv.x = rotated_u + pivot_u
            loop[uv_layer].uv.y = rotated_v + pivot_v

    # Update the mesh data
    bmesh.update_edit_mesh(me)



def triangles_count():
    """Counts the total number of triangles in the selected mesh objects."""

    selected_objects = bpy.context.selected_objects
    num_triangles = 0

    if not selected_objects:  
        return 0

    depsgraph = bpy.context.evaluated_depsgraph_get()

    for obj in selected_objects:
        if obj.type == 'MESH':
            mesh = obj.evaluated_get(depsgraph).to_mesh()
            num_triangles += sum(1 for poly in mesh.polygons if len(poly.vertices) == 3)
            obj.to_mesh_clear() 

    return num_triangles

def selected_vertexs(obj):
    # Get a bmesh representation of the mesh data in Edit Mode
    me = obj.data
    bm = bmesh.from_edit_mesh(me) 
    vertex_list = []

    for vertex in bm.verts:
        if vertex.select:
            vertex_list.append(vertex.index)
            
    # Important: Update the mesh data (if you modified the bmesh)
    bmesh.update_edit_mesh(me)
    return vertex_list

def select_vertexs(obj, vertex_list):
    # if obj.type != 'MESH':
    #     print(f"Error: Object '{obj.name}' is not a mesh.")
    #     return

    # if obj.mode != 'EDIT':
    #     print("Object is not in Edit Mode")
    #     return
    if obj.mode != 'EDIT':
        return  # Do nothing if not in Edit Mode

    me = obj.data
    bm = bmesh.from_edit_mesh(me)

    for i in vertex_list:
        try:
            bm.verts.ensure_lookup_table() 
            vertex = bm.verts[i]
            vertex.select = True
            bm.select_flush(True)  # Important: Flush selection changes

        except IndexError:
            print(f"Error: Vertex index {i} is out of range.")
    bmesh.update_edit_mesh(me)
            
            
def move_selected_vertices(obj, target_position=(0.0, 0.0, 0.0)):
    me = obj.data
    bm = bmesh.from_edit_mesh(me)

    for vert in bm.verts:
        if vert.select:
            try:
                vert.co = target_position  # Directly set the vertex location
            except:
                pass

    bmesh.update_edit_mesh(me)

def active_vertex():
    obj = bpy.context.active_object
    me = obj.data
    bm = bmesh.from_edit_mesh(me)

    try:
        active_vertex_index = bm.select_history.active.index
        active_vertex_co = bm.verts[active_vertex_index].co
        print(f"Active Vertex Index: {active_vertex_index}")
        print(f"Active Vertex Coordinates: {active_vertex_co}")
        return active_vertex_index, active_vertex_co

    except (AttributeError, IndexError):
        print("Error: No active vertex selected.")
        return None, None

    bmesh.update_edit_mesh(me)

def edge_angle(e1, e2, face_normal):
    up = Vector((0, 0, 1))
    #Cr. batFINGER : https://blender.stackexchange.com/a/203355
    b = set(e1.verts).intersection(e2.verts).pop()
    a = e1.other_vert(b).co - b.co
    c = e2.other_vert(b).co - b.co
    a.negate()    
    axis = a.cross(c).normalized()
    if axis.length < 1e-5:
        return pi # inline vert
    
    if axis.dot(face_normal) < 0:
        axis.negate()
    M = axis.rotation_difference(up).to_matrix().to_4x4()  

    a = (M @ a).xy.normalized()
    c = (M @ c).xy.normalized()
    
    return pi - atan2(a.cross(c), a.dot(c))