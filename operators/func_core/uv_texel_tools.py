import bpy
import bmesh

from math import sqrt
from mathutils import Matrix, Vector
from contextlib import contextmanager
import math


# -------------------------------------------------
# Texel Density utilities
# -------------------------------------------------

def _poly_area_2d(pts):
    area = 0.0
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        area += x1 * y2 - x2 * y1
    return abs(area) * 0.5


def _gather_selection(obj):
    """Gather geometry + UV selection respecting Edit Mode & UV Sync.
    Returns (world_area, uv_area, uv_loops_to_transform)"""
    me = obj.data
    in_edit = (bpy.context.mode == 'EDIT_MESH' and bpy.context.object == obj)
    uv_sync = bpy.context.scene.tool_settings.use_uv_select_sync if in_edit else False

    if in_edit:
        bm = bmesh.from_edit_mesh(me)
        free_after = False
    else:
        bm = bmesh.new()
        bm.from_mesh(me)
        free_after = True

    bm.faces.ensure_lookup_table()
    uv_layer = bm.loops.layers.uv.active
    if not uv_layer:
        if free_after:
            bm.free()
        raise RuntimeError("Active UV map not found")

    if in_edit:
        if uv_sync:
            # Face selection defines UV selection
            any_face_sel = any(f.select for f in bm.faces)
            faces = [f for f in bm.faces if (f.select if any_face_sel else True)]
            uv_loops = [l[uv_layer].uv for f in faces for l in f.loops]
        else:
            # UV loop selection explicitly
            uv_loops = [l[uv_layer].uv for f in bm.faces for l in f.loops if l[uv_layer].select]
            faces = [f for f in bm.faces if any(l[uv_layer].select for l in f.loops)] or bm.faces[:]
    else:
        any_face_sel = any(f.select for f in bm.faces)
        faces = [f for f in bm.faces if (f.select if any_face_sel else True)]
        uv_loops = [l[uv_layer].uv for f in faces for l in f.loops]

    world_area = 0.0
    uv_area = 0.0
    for f in faces:
        world_area += f.calc_area()
        poly = [l[uv_layer].uv.copy() for l in f.loops]
        # local polygon area function (shoelace)
        area = 0.0
        n = len(poly)
        for i in range(n):
            x1, y1 = poly[i]
            x2, y2 = poly[(i + 1) % n]
            area += x1 * y2 - x2 * y1
        uv_area += abs(area) * 0.5

    if free_after:
        bm.free()

    return world_area, uv_area, uv_loops


def compute_texel_density(obj, texture_size: int) -> float:
    """Average texel density (px per Blender unit) for selected faces or whole mesh.
    TD = texture_size * sqrt(sum(UV_area) / sum(world_area))
    """
    world_area, uv_area, _ = _gather_selection(obj)
    if world_area <= 0.0:
        raise RuntimeError("No geometry or zero area")
    return float(texture_size) * sqrt(uv_area / world_area)


def set_texel_density(obj, target_px_per_unit: float, texture_size: int):
    """Scale UVs around selection centroid to reach target px per unit.
    Works in OBJECT or EDIT_MESH without leaving the current mode."""
    current = compute_texel_density(obj, texture_size)
    if current <= 0.0:
        raise RuntimeError("Current texel density is zero")
    scale = target_px_per_unit / current

    me = obj.data
    in_edit = (bpy.context.mode == 'EDIT_MESH' and bpy.context.object == obj)

    if in_edit:
        bm = bmesh.from_edit_mesh(me)
        free_after = False
    else:
        bm = bmesh.new()
        bm.from_mesh(me)
        free_after = True

    bm.faces.ensure_lookup_table()
    uv_layer = bm.loops.layers.uv.active
    if not uv_layer:
        if free_after:
            bm.free()
        raise RuntimeError("Active UV map not found")

    # Reuse the same selection logic to get the exact UV loops to transform
    _, _, uvs = _gather_selection(obj)
    if not uvs:
        if free_after:
            bm.free()
        return

    c = Vector((sum(u.x for u in uvs)/len(uvs), sum(u.y for u in uvs)/len(uvs)))
    for uv in uvs:
        uv[:] = c + (uv - c) * scale

    if in_edit:
        bmesh.update_edit_mesh(me, loop_triangles=False, destructive=False)
    else:
        bm.to_mesh(me)
        me.update()
        bm.free()
