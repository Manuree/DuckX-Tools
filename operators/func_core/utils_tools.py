import bpy
import bmesh

import urllib.request
import zipfile
import os
import subprocess
import json
import textwrap
from math import radians, cos, sin, degrees, atan2, pi
from math import sqrt
from mathutils import Matrix, Vector
from contextlib import contextmanager
from contextlib import suppress
import math



# Select Tools Function
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

def objects_to_list():
    items = []
    selected_objects = bpy.context.selected_objects
    for obj in selected_objects:
        items.append(obj.name)
    return items

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

def select_face_by_index(obj, face_index):
    if obj.type != 'MESH':
        print(f"{obj.name} is not a mesh object")
        return
    bpy.ops.object.mode_set(mode='OBJECT')
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.faces.ensure_lookup_table()
    for face in bm.faces:
        face.select = False
    if face_index < len(bm.faces):
        bm.faces[face_index].select = True
        print(f"Selected face index: {face_index}")
    else:
        print(f"Face index {face_index} out of range")
    
    bm.to_mesh(mesh)
    bm.free()
    bpy.ops.object.mode_set(mode='EDIT')

def select_vertex_by_index(obj, vertex_index):
    if obj.type != 'MESH':
        print(f"{obj.name} is not a mesh object")
        return
    bpy.ops.object.mode_set(mode='OBJECT')
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    for vex in bm.verts:
        vex.select = False
    if vertex_index < len(bm.verts):
        bm.verts[vertex_index].select = True
        print(f"Selected face index: {vertex_index}")
    else:
        print(f"Face index {vertex_index} out of range")
    
    bm.to_mesh(mesh)
    bm.free()
    bpy.ops.object.mode_set(mode='EDIT')

def select_edge_by_index(obj, edge_index):
    if obj.type != 'MESH':
        print(f"{obj.name} is not a mesh object")
        return
    bpy.ops.object.mode_set(mode='OBJECT')
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.edges.ensure_lookup_table()
    for edge in bm.edges:
        edge.select = False
    if edge_index < len(bm.edges):
        bm.edges[edge_index].select = True
        print(f"Selected face index: {edge_index}")
    else:
        print(f"Face index {edge_index} out of range")
    
    bm.to_mesh(mesh)
    bm.free()
    bpy.ops.object.mode_set(mode='EDIT')    



# 3D Cursor Tools
def store_cursor_position():
    cursor = bpy.context.scene.cursor
    
    cursor_data = {
        'location': cursor.location.copy(),
        'rotation_euler': cursor.rotation_euler.copy()
    }
    return cursor_data

def restore_cursor_position(cursor_data):
    if not cursor_data or 'location' not in cursor_data:
        return False
    
    try:
        cursor = bpy.context.scene.cursor
        
        # Restore location
        cursor.location = cursor_data['location']
        
        # Restore rotation if available
        if 'rotation_euler' in cursor_data:
            cursor.rotation_euler = cursor_data['rotation_euler']
        return True
        
    except Exception as e:
        print(f"Error restoring cursor position: {str(e)}")
        return False

def get_cursor_location():
    return bpy.context.scene.cursor.location.copy()

def set_cursor_location(location):
    try:
        if isinstance(location, (list, tuple)):
            location = Vector(location)
        
        bpy.context.scene.cursor.location = location
        return True
        
    except Exception as e:
        print(f"Error setting cursor location: {str(e)}")
        return False

def reset_cursor_to_origin():
    try:
        cursor = bpy.context.scene.cursor
        cursor.location = (0.0, 0.0, 0.0)
        cursor.rotation_euler = (0.0, 0.0, 0.0)
        return True
        
    except Exception as e:
        print(f"Error resetting cursor: {str(e)}")
        return False

#Object data tools
def compare_colors(color1, color2):
    # Define a tolerance for floating-point comparisons
    epsilon = 0.001

    # Compare each component of the color tuple
    for c1, c2 in zip(color1, color2):
        if abs(c1 - c2) > epsilon:
            return False

    return True

def refresh_panel():
    for area in bpy.context.workspace.screens[0].areas:
                if area.type == 'VIEW_3D':
                    for region in area.regions:
                        if region.type == 'UI':
                            region.tag_redraw()
                            break

def message_box(message = "", title = "Message Box", icon = 'INFO'):
    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

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