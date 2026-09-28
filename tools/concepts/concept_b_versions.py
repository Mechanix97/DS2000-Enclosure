"""Concept B (frame) in two versions around the Choc board: flat on the desk, and on a separate 7 deg
wedge. The same tray serves both: it has rubber-foot recesses for the flat version and 6 x 1.5 mm
magnet pockets under the corner bosses, matched by pockets in the wedge's top face.
"""
import math, os, sys
import numpy as np
import pyvista as pv
from build123d import Pos, Box, Cylinder, Polyline, make_face, extrude, Plane, export_step
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from concepts import (slab, concept_b, board_meshes, mesh_of, screws, HOLES, FLOOR_Z, OUT, HERE)

TILT = 7.0
W, D = 78.0, 52.0
H_FRONT = 3.0
H_BACK = H_FRONT + D * math.tan(math.radians(TILT))
MAGNET = (3.1, 1.6)                     # pocket radius, depth: 6 x 1.5 mm disc magnets

def tray():
    t = concept_b()
    for x, y in HOLES:
        t -= Pos(x, y, FLOOR_Z + MAGNET[1] / 2 - 0.01) * Cylinder(*MAGNET)
    return t

def tilt_matrix():
    """Tray frame -> desk frame: the tray's front-bottom edge rests on the wedge's front-top edge."""
    a = math.radians(TILT)
    rx = np.array([[1, 0, 0, 0], [0, math.cos(a), -math.sin(a), 0], [0, math.sin(a), math.cos(a), 0], [0, 0, 0, 1]])
    t1 = np.eye(4); t1[:3, 3] = (0, D / 2, -FLOOR_Z)
    t2 = np.eye(4); t2[:3, 3] = (0, -D / 2, H_FRONT)
    return t2 @ rx @ t1

def wedge():
    prof = make_face(Polyline((-D / 2, 0), (D / 2, 0), (D / 2, H_BACK), (-D / 2, H_FRONT), close=True))
    w = extrude(Plane.YZ.offset(-W / 2) * prof, amount=W)
    w = w & slab(W, D, 6, -1, H_BACK + 1)
    m = tilt_matrix()
    for x, y in HOLES:                  # magnet pockets under the tray's, normal to the sloped face
        p = m @ np.array([x, y, FLOOR_Z, 1.0])
        from build123d import Location
        loc = Location((p[0], p[1], p[2]), (TILT, 0, 0))
        w -= loc * Pos(0, 0, -MAGNET[1] / 2 + 0.01) * Cylinder(*MAGNET)
    for x, y in [(-30, -19), (30, -19), (-30, 19), (30, 19)]:
        w -= Pos(x, y, 0.3) * Cylinder(4.0, 0.6)        # rubber feet
    return w

VIEWS = {
    "iso": dict(position=(-80, -125, 175), focal=(0, 2, 4), up=(0, 0, 1)),
    "side": dict(position=(-200, -10, 18), focal=(0, 0, 4), up=(0, 0, 1)),
    "back": dict(position=(75, 155, 85), focal=(0, 0, 2), up=(0, 0, 1)),
}
TRAY_COL, WEDGE_COL = (0.93, 0.92, 0.89), (0.30, 0.31, 0.33)

def render(name, board, tray_mesh, wedge_mesh=None, m=None):
    for view, cam in VIEWS.items():
        pl = pv.Plotter(off_screen=True, window_size=(1600, 1050))
        pl.set_background((0.93, 0.93, 0.94), top=(0.82, 0.83, 0.86))
        def add(mesh, **kw):
            if mesh is None:
                return
            mesh = mesh.copy()
            if m is not None:
                mesh = mesh.transform(m, inplace=False)
            elif wedge_mesh is None:
                mesh = mesh.translate((0, 0, -FLOOR_Z), inplace=False)      # flat: tray on the desk at z=0
            pl.add_mesh(mesh, smooth_shading=True, **kw)
        for mm_, c in board:
            add(mm_, color=c, specular=0.25)
        for sc in screws():
            add(mesh_of(sc), color=(0.7, 0.7, 0.72), specular=0.8)
        add(tray_mesh, color=TRAY_COL, specular=0.2)
        if wedge_mesh is not None:
            pl.add_mesh(wedge_mesh, color=WEDGE_COL, smooth_shading=True, specular=0.3)
        pl.add_mesh(pv.Plane(center=(0, 0, -0.05), i_size=400, j_size=400), color=(0.86, 0.86, 0.87))
        pl.enable_anti_aliasing("ssaa")
        pl.camera.position, pl.camera.focal_point, pl.camera.up = cam["position"], cam["focal"], cam["up"]
        pl.camera.view_angle = 24
        pl.screenshot(os.path.join(OUT, f"{name}_{view}.png"))
        pl.close()

if __name__ == "__main__":
    board = board_meshes(os.path.join(HERE, sys.argv[1] if len(sys.argv) > 1 else "pcb_render.step"))
    t = tray(); w = wedge()
    tb, wb = t.bounding_box(), w.bounding_box()
    print(f"tray {tb.size.X:.1f} x {tb.size.Y:.1f} x {tb.size.Z:.1f}, wedge {wb.size.X:.1f} x {wb.size.Y:.1f}, "
          f"{H_FRONT:.1f} -> {H_BACK:.1f} mm")
    export_step(t, os.path.join(OUT, "B_tray.step")); export_step(w, os.path.join(OUT, "B_wedge.step"))
    tm = mesh_of(t, 0.03)
    render("B_flat", board, tm)
    render("B_tilt", board, tm, mesh_of(w, 0.03), tilt_matrix())
    print("done")
