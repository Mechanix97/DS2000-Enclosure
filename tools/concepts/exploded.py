import os, sys
import pyvista as pv
from build123d import Pos, Cylinder
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from concepts import board_meshes, mesh_of, HOLES, OUT, HERE
from concept_b_versions import tray, wedge, TRAY_COL, WEDGE_COL

board = board_meshes(os.path.join(HERE, "pcb_render.step"))
t, w = mesh_of(tray(), 0.03), mesh_of(wedge(), 0.03)
pl = pv.Plotter(off_screen=True, window_size=(1800, 1500))
pl.set_background((0.95, 0.95, 0.96), top=(0.84, 0.85, 0.88))
BASE = 9.4 + 6.5            # wedge on the desk, tray lifted above it
DZ_TRAY, DZ_BOARD, DZ_SCREW = 22, 44, 62
pl.add_mesh(w, color=WEDGE_COL, smooth_shading=True, specular=0.3)
pl.add_mesh(t.translate((0, 0, DZ_TRAY), inplace=False), color=TRAY_COL, smooth_shading=True, specular=0.2)
for m, c in board:
    if m is not None:
        pl.add_mesh(m.translate((0, 0, DZ_BOARD), inplace=False), color=c, smooth_shading=True, specular=0.25)
for x, y in HOLES:
    s = mesh_of(Pos(x, y, 1.6 + 0.65) * Cylinder(1.9, 1.3) + Pos(x, y, 1.6 - 3.0) * Cylinder(1.0, 6.0))
    pl.add_mesh(s.translate((0, 0, DZ_SCREW), inplace=False), color=(0.72, 0.72, 0.74), smooth_shading=True, specular=0.8)
    pl.add_mesh(pv.Line((x, y, 8), (x, y, DZ_SCREW - 4)), color=(0.55, 0.55, 0.6), line_width=2)
for x, y in HOLES:           # magnets between tray and wedge
    pl.add_mesh(mesh_of(Pos(x, y, 13) * Cylinder(3.0, 1.5)), color=(0.6, 0.62, 0.66), smooth_shading=True, specular=0.9)
pl.enable_anti_aliasing("ssaa")
pl.camera.position, pl.camera.focal_point, pl.camera.up = (-120, -190, 150), (0, 0, 30), (0, 0, 1)
pl.camera.view_angle = 26
pl.screenshot(os.path.join(OUT, "exploded.png"))
print("ok")
