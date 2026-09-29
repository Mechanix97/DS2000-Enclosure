"""DS2000 enclosure: concept B tray, generated in Fusion 360.

Run from Scripts and Add-Ins (Utilities > Add-Ins). It imports the rev A board as a reference and
builds the tray around it, in millimetres, with the same axes as pcb/DS2000-PCB-revA.step: origin at
the board's centre on its bottom face, +Y to the back (USB-C), Z up, board top face at Z = 1.6.

Dimensions come from tools/concepts/concepts.py (concept B) and docs/requirements.md. Change the
constants below and run again on a new design to try another value. Set Fusion's default modelling
orientation to Z up first (Preferences > General), or the model looks rotated (the coordinates are fine).
"""
import math
import os
import traceback

import adsk.core
import adsk.fusion

# ---- dimensions (mm) --------------------------------------------------------------------------
BOARD_T = 1.6
LIP = 0.6                                   # frame lip above the board's top face
TOP_Z = BOARD_T + LIP                       # 2.2
FLOOR_Z = -6.5                              # tray bottom (4.5 mm pocket + 2 mm floor)
POCKET_Z = -4.5                             # pocket floor
OUTER = (78.0, 52.0, 6.0)                   # frame width, depth, corner radius
SEAT = (72.4, 46.4, 3.2)                    # board seat (board 72 x 46 + 0.2 clearance a side)
SEAT_TOP = TOP_Z + 0.1
POCKET = (68.0, 42.0, 1.2)
HOLES = [(-32, 19), (32, 19), (-32, -19), (32, -19)]
BOSS_R = 3.0
INSERT_R, INSERT_DEPTH = 1.6, 4.0           # M2 heat-set insert
MAGNET_R, MAGNET_DEPTH = 3.1, 1.6           # 6 x 1.5 mm disc magnet, for the 7 deg wedge
FEET = [(-24, -14), (24, -14), (-24, 14), (24, 14)]   # 2.3 mm clear of the magnet pockets
FOOT_R, FOOT_DEPTH = 4.0, 0.6               # rubber-foot recess
USB_PLUG = (13.0, 18.0, 26.0, -5.5, 1.5)    # width, y0, y1, z0, z1: plug and receptacle
USB_WALL = (13.0, 22.0, 28.0, -2.5, 2.5)    # through the back wall of the frame
FILLET_TOP, CHAMFER_BOTTOM = 1.0, 0.8
BOARD_STEP = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                          "..", "..", "..", "pcb", "DS2000-PCB-revA.step"))

P = adsk.core.Point3D.create
CM = 0.1                                    # Fusion's API works in cm


def rounded_rect(sk, w, h, r):
    """Closed rectangle w x h with corner radius r, centred on the sketch origin (all in mm)."""
    x, y, r, s = w / 2 * CM, h / 2 * CM, r * CM, math.sqrt(0.5)
    L, A = sk.sketchCurves.sketchLines, sk.sketchCurves.sketchArcs
    l1 = L.addByTwoPoints(P(-x + r, -y, 0), P(x - r, -y, 0))
    a1 = A.addByThreePoints(l1.endSketchPoint, P(x - r + r * s, -y + r - r * s, 0), P(x, -y + r, 0))
    l2 = L.addByTwoPoints(a1.endSketchPoint, P(x, y - r, 0))
    a2 = A.addByThreePoints(l2.endSketchPoint, P(x - r + r * s, y - r + r * s, 0), P(x - r, y, 0))
    l3 = L.addByTwoPoints(a2.endSketchPoint, P(-x + r, y, 0))
    a3 = A.addByThreePoints(l3.endSketchPoint, P(-x + r - r * s, y - r + r * s, 0), P(-x, y - r, 0))
    l4 = L.addByTwoPoints(a3.endSketchPoint, P(-x, -y + r, 0))
    A.addByThreePoints(l4.endSketchPoint, P(-x + r - r * s, -y + r - r * s, 0), l1.startSketchPoint)


def extrude(comp, sk, z0, z1, op):
    """Extrude every profile of sk from Z = z0 to Z = z1 (mm), the sketch being on the XY plane."""
    profs = adsk.core.ObjectCollection.create()
    for i in range(sk.profiles.count):
        profs.add(sk.profiles.item(i))
    inp = comp.features.extrudeFeatures.createInput(profs, op)
    inp.startExtent = adsk.fusion.OffsetStartDefinition.create(adsk.core.ValueInput.createByReal(z0 * CM))
    inp.setDistanceExtent(False, adsk.core.ValueInput.createByReal((z1 - z0) * CM))
    return comp.features.extrudeFeatures.add(inp)


def sketch(comp, name):
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.name = name
    return sk


def circles(sk, centres, r):
    for cx, cy in centres:
        sk.sketchCurves.sketchCircles.addByCenterRadius(P(cx * CM, cy * CM, 0), r * CM)


def rect(sk, w, y0, y1):
    sk.sketchCurves.sketchLines.addTwoPointRectangle(P(-w / 2 * CM, y0 * CM, 0), P(w / 2 * CM, y1 * CM, 0))


def planar_face_edges(body, z):
    """Edges of the largest planar face lying at Z = z (mm)."""
    best = None
    for f in body.faces:
        bb = f.boundingBox
        if f.geometry.surfaceType == adsk.core.SurfaceTypes.PlaneSurfaceType \
                and abs(bb.minPoint.z - z * CM) < 1e-4 and abs(bb.maxPoint.z - z * CM) < 1e-4:
            if best is None or f.area > best.area:
                best = f
    edges = adsk.core.ObjectCollection.create()
    for e in best.edges:
        edges.add(e)
    return edges


def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface
    try:
        if app.preferences.generalPreferences.defaultModelingOrientation != \
                adsk.core.DefaultModelingOrientations.ZUpModelingOrientation:
            ui.messageBox("Fusion is set to Y up: the model will look rotated (it is correct in XYZ).\n"
                          "Set Preferences > General > Default modeling orientation to Z up for a new design.")
        design = adsk.fusion.Design.cast(app.activeProduct)
        if design is None:
            ui.messageBox("Open a Fusion design first (File > New Design).")
            return
        root = design.rootComponent

        try:                                                 # an assembly design: the tray is a component
            comp = root.occurrences.addNewComponent(adsk.core.Matrix3D.create()).component
            comp.name = "DS2000 Tray"
            separate = True
        except RuntimeError:                                 # a part design has no components
            comp, separate = root, False
        new, join, cut = (adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
                          adsk.fusion.FeatureOperations.JoinFeatureOperation,
                          adsk.fusion.FeatureOperations.CutFeatureOperation)

        # frame: outer block, soft top edge and chamfered bottom edge
        sk = sketch(comp, "Outer")
        rounded_rect(sk, *OUTER)
        body = extrude(comp, sk, FLOOR_Z, TOP_Z, new).bodies.item(0)
        body.name = "Tray"
        fil = comp.features.filletFeatures.createInput()
        fil.addConstantRadiusEdgeSet(planar_face_edges(body, TOP_Z),
                                     adsk.core.ValueInput.createByReal(FILLET_TOP * CM), True)
        comp.features.filletFeatures.add(fil)
        cha = comp.features.chamferFeatures.createInput2()
        cha.chamferEdgeSets.addEqualDistanceChamferEdgeSet(
            planar_face_edges(body, FLOOR_Z), adsk.core.ValueInput.createByReal(CHAMFER_BOTTOM * CM), True)
        comp.features.chamferFeatures.add(cha)

        # board seat and the pocket under it
        sk = sketch(comp, "Board seat")
        rounded_rect(sk, *SEAT)
        extrude(comp, sk, 0.0, SEAT_TOP, cut)
        sk = sketch(comp, "Pocket")
        rounded_rect(sk, *POCKET)
        extrude(comp, sk, POCKET_Z, 0.1, cut)

        # four M2 bosses with heat-set insert holes
        sk = sketch(comp, "Bosses")
        circles(sk, HOLES, BOSS_R)
        extrude(comp, sk, POCKET_Z, 0.0, join)
        sk = sketch(comp, "Insert holes")
        circles(sk, HOLES, INSERT_R)
        extrude(comp, sk, -INSERT_DEPTH, 0.0, cut)

        # USB-C: cut-out for the plug and receptacle, and through the back wall
        for name, (w, y0, y1, z0, z1) in (("USB plug", USB_PLUG), ("USB wall", USB_WALL)):
            sk = sketch(comp, name)
            rect(sk, w, y0, y1)
            extrude(comp, sk, z0, z1, cut)

        # underside: magnet pockets (7 deg wedge) and rubber-foot recesses
        sk = sketch(comp, "Magnet pockets")
        circles(sk, HOLES, MAGNET_R)
        extrude(comp, sk, FLOOR_Z, FLOOR_Z + MAGNET_DEPTH, cut)
        sk = sketch(comp, "Feet")
        circles(sk, FEET, FOOT_R)
        extrude(comp, sk, FLOOR_Z, FLOOR_Z + FOOT_DEPTH, cut)

        # the board goes in last, as a reference, so no cut above can touch it; only into its own component
        if separate and os.path.isfile(BOARD_STEP):
            app.importManager.importToTarget(app.importManager.createSTEPImportOptions(BOARD_STEP), root)

        app.activeViewport.fit()
    except Exception:
        if ui:
            ui.messageBox("DS2000 Tray failed:\n{}".format(traceback.format_exc()))
