import bpy
import bmesh

from math import radians, cos, sin, degrees, atan2, pi
from math import sqrt
from mathutils import Matrix, Vector
from contextlib import contextmanager
import math




# -------------------------------------------------
# UV Tools
# -------------------------------------------------

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