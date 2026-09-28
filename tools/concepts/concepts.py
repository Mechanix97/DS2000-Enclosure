"""Three flat enclosure concepts around the DS2000 rev A board, rendered for comparison.

Axes as pcb/DS2000-PCB-revA.step: origin at the board centre on its bottom face, +Y to the back
(USB-C), Z up; board top at Z = 1.6.
"""
import os, sys
import numpy as np
import pyvista as pv
from build123d import (Location, Box, BuildPart, Cylinder, Locations, Mode, Pos, RectangleRounded, Plane,
                       extrude, import_step, chamfer, fillet, Axis, Compound, export_step)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out"); os.makedirs(OUT, exist_ok=True)
HOLES = [(-32, 19), (32, 19), (-32, -19), (32, -19)]
FLOOR_Z, POCKET_Z = -6.5, -4.5                     # tray bottom, pocket floor (4.5 mm under the board)

def slab(w, h, r, z0, z1):
    return Pos(0, 0, z0) * extrude(RectangleRounded(w, h, r), amount=z1 - z0)

def bosses_and_usb(tray, top_z=0.0):
    for x, y in HOLES:
        tray += Pos(x, y, POCKET_Z) * Cylinder(3.0, top_z - POCKET_Z, align=None) \
            if False else Pos(x, y, (POCKET_Z + top_z) / 2) * Cylinder(3.0, top_z - POCKET_Z)
        tray -= Pos(x, y, top_z - 2.0) * Cylinder(1.6, 4.0)          # M2 heat-set insert
    tray -= Pos(0, 22.0, -2.0) * Box(13.0, 8.0, 7.0)                 # USB-C plug and receptacle
    for x, y in [(-27, -14), (27, -14), (-27, 14), (27, 14)]:        # rubber feet
        tray -= Pos(x, y, FLOOR_Z + 0.3) * Cylinder(4.0, 0.6)
    return tray

def concept_a():
    """Monolith: the tray follows the board outline exactly."""
    t = slab(72, 46, 3, FLOOR_Z, 0.0)
    t = chamfer(t.edges().group_by(Axis.Z)[0], 0.8)                  # soft bottom edge, outline only
    t -= slab(68, 42, 1.2, POCKET_Z, 0.1)
    return bosses_and_usb(t)

def concept_b():
    """Frame: a 3 mm bezel with a lip 0.6 mm above the board, which sits recessed in it."""
    lip = 1.6 + 0.6
    t = slab(78, 52, 6, FLOOR_Z, lip)
    t = fillet(t.edges().group_by(Axis.Z)[-1], 1.0)                  # rounded top of the frame
    t = chamfer(t.edges().group_by(Axis.Z)[0], 0.8)
    t -= slab(72.4, 46.4, 3.2, 0.0, lip + 0.1)                         # board seat
    t -= slab(68, 42, 1.2, POCKET_Z, 0.1)
    t = bosses_and_usb(t)
    t -= Pos(0, 25.0, 0.0) * Box(13.0, 6.0, 5.0)                     # USB through the frame
    return t

def concept_c():
    """Floating on columns: a smoked base smaller than the board, four round standoffs at the
    corners, the board hovering above with its underside (and debug pads) in view."""
    base_top = FLOOR_Z + 3.0
    t = slab(60, 34, 4, FLOOR_Z, base_top)
    t = fillet(t.edges().group_by(Axis.Z)[-1], 1.0)
    for x, y in HOLES:
        t += Pos(x, y, (base_top - 1.0 + 0.0) / 2) * Cylinder(3.2, 0.0 - (base_top - 1.0))
        t += Pos(x, y, base_top - 1.5) * Cylinder(4.2, 3.0)          # foot under each column
        t -= Pos(x, y, -2.0) * Cylinder(1.6, 4.0)                    # M2 heat-set insert
    for x, y in [(-22, -10), (22, -10), (-22, 10), (22, 10)]:
        t -= Pos(x, y, FLOOR_Z + 0.3) * Cylinder(4.0, 0.6)
    return t

# ---------------------------------------------------------------- board meshes
GOLD, BLACK, WHITE = (0.86, 0.70, 0.30), (0.06, 0.06, 0.07), (0.96, 0.96, 0.96)
def board_meshes(step):
    s = import_step(step)
    out = []
    def colour_for(label, col):
        if label in ("DS2000_copper", "DS2000_pad", "DS2000_via"):
            return GOLD
        if label == "DS2000_PCB":
            return (0.12, 0.12, 0.12)
        if label == "DS2000_soldermask":
            return BLACK
        if label == "DS2000_silkscreen":
            return WHITE
        if col is None:
            return (0.5, 0.5, 0.5)
        rgba = col.to_tuple() if hasattr(col, "to_tuple") else tuple(col)
        return tuple(rgba[:3])
    def walk(n, label, loc):
        lab = getattr(n, "label", "") or label
        ch = getattr(n, "children", [])
        if ch:
            for c in ch:                    # instanced parts: the placement lives on the parent
                walk(c, lab, loc * n.location)
            return
        col = getattr(n, "color", None)
        for sol in (n.solids() or [n]):
            out.append((mesh_of(loc * sol), colour_for(lab, col)))
    walk(s, "", Location())
    return out

def mesh_of(shape, tol=0.02):
    verts, tris = shape.tessellate(tol, 0.3)
    if not tris:
        return None
    pts = np.array([[v.X, v.Y, v.Z] for v in verts])
    faces = np.hstack([[3, *t] for t in tris])
    return pv.PolyData(pts, faces)

TRAY_STYLE = {
    "A": dict(color=(0.10, 0.10, 0.11), opacity=1.0, specular=0.3),
    "B": dict(color=(0.93, 0.92, 0.89), opacity=1.0, specular=0.2),
    "C": dict(color=(0.20, 0.21, 0.23), opacity=0.55, specular=0.6),
}
VIEWS = {
    "iso": dict(position=(-75, -120, 165), focal=(0, 2, 2), up=(0, 0, 1)),
    "back": dict(position=(70, 150, 75), focal=(0, 0, 0), up=(0, 0, 1)),
    "side": dict(position=(-190, -40, 25), focal=(0, 0, 5), up=(0, 0, 1)),
}

def screws():
    return [Pos(x, y, 1.6 + 0.65) * Cylinder(1.9, 1.3) for x, y in HOLES]

def render(name, tray, board):
    tray_mesh = mesh_of(tray, 0.03)
    for view, cam in VIEWS.items():
        pl = pv.Plotter(off_screen=True, window_size=(1600, 1050))
        pl.set_background((0.93, 0.93, 0.94), top=(0.82, 0.83, 0.86))
        for m, c in board:
            if m is not None:
                pl.add_mesh(m, color=c, smooth_shading=True, specular=0.25)
        for sc in screws():
            pl.add_mesh(mesh_of(sc), color=(0.7, 0.7, 0.72), smooth_shading=True, specular=0.8)
        pl.add_mesh(tray_mesh, smooth_shading=True, **TRAY_STYLE[name])
        pl.enable_anti_aliasing("ssaa")
        pl.camera.position, pl.camera.focal_point, pl.camera.up = cam["position"], cam["focal"], cam["up"]
        pl.camera.view_angle = 24
        pl.screenshot(os.path.join(OUT, f"{name}_{view}.png"))
        pl.close()

if __name__ == "__main__":
    board = board_meshes(os.path.join(HERE, "pcb_render.step"))
    print("board meshes", len(board))
    for name, fn in [("A", concept_a), ("B", concept_b), ("C", concept_c)]:
        tray = fn()
        bb = tray.bounding_box()
        print(name, f"{bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f} mm, volume {tray.volume/1000:.1f} cm3")
        export_step(tray, os.path.join(OUT, f"tray_{name}.step"))
        render(name, tray, board)
    print("done")
