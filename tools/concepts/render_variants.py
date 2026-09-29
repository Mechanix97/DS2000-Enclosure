"""Product renders of the DS2000 (concept B on its 7 deg wedge) in three colourways, for mechardo3d.

Writes out/site/<variant>-<view>.png at 1536 x 1024 on the site's gallery background (#f2f3f0).
"""
import os, sys
import numpy as np
import pyvista as pv
from build123d import Pos, Cylinder
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from concepts import board_meshes, mesh_of, HOLES, OUT, HERE
from concept_b_versions import tray, wedge, tilt_matrix

BG = (0xf2 / 255, 0xf3 / 255, 0xf0 / 255)
KEY_X = (-18.0, 0.0, 18.0)                       # MUTE, DEAFEN, DISCONNECT (board frame)

def hexc(h):
    return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))

VARIANTS = {
    "negro": dict(tray=hexc("#141416"), wedge=hexc("#0c0c0d"), keys=[hexc("#1b1b1d")] * 3,
                  screw=hexc("#2a2a2c"), spec=0.35),
    "original": dict(tray=hexc("#ede9e1"), wedge=hexc("#4d4f54"), keys=[hexc("#eeeeea")] * 3,
                     screw=hexc("#b4b4b8"), spec=0.2),
    # North American Super Nintendo: light grey shell, dark grey base, lavender X/Y buttons for
    # MUTE and DEAFEN and the deep purple of A/B for DISCONNECT
    "snes": dict(tray=hexc("#c8c6cd"), wedge=hexc("#56545c"),
                 keys=[hexc("#a9a3d3"), hexc("#a9a3d3"), hexc("#4f3f8f")],
                 screw=hexc("#9a9aa2"), spec=0.25),
}

VIEWS = {   # camera position, focal point, view angle
    "frente": ((-95, -150, 120), (0, 4, 6), 22),
    "trasera": ((85, 165, 95), (0, 2, 4), 22),
    "superior": ((0, -22, 230), (0, 0, 6), 22),
    "explotada": ((-150, -235, 125), (0, 0, 22), 25),
}

def is_keycap(mesh, col):
    return abs(col[0] - 0.93) < 0.03 and abs(col[1] - 0.93) < 0.03 and mesh.bounds[4] > 7.0

def main():
    board = [(m, c) for m, c in board_meshes(os.path.join(HERE, "pcb_render.step")) if m is not None]
    t_mesh, w_mesh = mesh_of(tray(), 0.02), mesh_of(wedge(), 0.02)
    screws = [mesh_of(Pos(x, y, 1.6 + 0.65) * Cylinder(1.9, 1.3)) for x, y in HOLES]
    M = tilt_matrix()
    out = os.path.join(OUT, "site"); os.makedirs(out, exist_ok=True)
    for vname, v in VARIANTS.items():
        for view, (pos, focal, angle) in VIEWS.items():
            exploded = view == "explotada"
            pl = pv.Plotter(off_screen=True, window_size=(1536, 1024), lighting="none")
            pl.set_background(BG)
            pl.add_light(pv.Light(position=(-120, -160, 260), focal_point=(0, 0, 0), intensity=0.85))
            pl.add_light(pv.Light(position=(160, 60, 140), focal_point=(0, 0, 0), intensity=0.35))
            pl.add_light(pv.Light(light_type="headlight", intensity=0.25))

            def place(mesh, dz=0.0):
                m = mesh.translate((0, 0, dz), inplace=False) if dz else mesh
                return m.transform(M, inplace=False) if not exploded else m
            dz_tray, dz_board = (22.0, 44.0) if exploded else (0.0, 0.0)
            for m, c in board:
                if is_keycap(m, c):
                    cx = (m.bounds[0] + m.bounds[1]) / 2
                    c = v["keys"][int(np.argmin([abs(cx - k) for k in KEY_X]))]
                    pl.add_mesh(place(m, dz_board), color=c, smooth_shading=True, specular=0.15, specular_power=12)
                else:
                    pl.add_mesh(place(m, dz_board), color=c, smooth_shading=True, specular=0.3)
            for s in screws:
                pl.add_mesh(place(s, dz_board + (18.0 if exploded else 0.0)), color=v["screw"], smooth_shading=True, specular=0.7)
            pl.add_mesh(place(t_mesh, dz_tray - (0.0 if exploded else 0.0)) if exploded else t_mesh.transform(M, inplace=False),
                        color=v["tray"], smooth_shading=True, ambient=0.22, diffuse=0.8, specular=v["spec"], specular_power=18)
            wm = w_mesh.translate((0, 0, -16.0), inplace=False) if exploded else w_mesh
            pl.add_mesh(wm, color=v["wedge"], smooth_shading=True, specular=v["spec"], specular_power=18)
            pl.enable_anti_aliasing("ssaa")
            pl.camera.position, pl.camera.focal_point, pl.camera.up = pos, focal, (0, 0, 1)
            pl.camera.view_angle = angle
            pl.screenshot(os.path.join(out, f"{vname}-{view}.png"))
            pl.close()
            print(vname, view, flush=True)

if __name__ == "__main__":
    main()
