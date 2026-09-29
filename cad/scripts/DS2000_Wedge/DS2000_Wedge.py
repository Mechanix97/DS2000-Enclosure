"""DS2000 enclosure: the 7 degree wedge for the concept B tray, generated in Fusion 360.

Run from Scripts and Add-Ins in a NEW design, not the tray's (the two share the origin and would cut
each other). Millimetres. The wedge is modelled on the desk: Z = 0 is its underside, Y = -26 its front
and +26 its back, so the top slopes up towards the back, where the USB-C is.

The tray sits on it with its front-bottom edge on the wedge's front-top edge, tilted 7 degrees. Its top
face takes the magnet pockets (under the tray's corner bosses) and the recesses for the pads glued to the
tray's underside, so the tray lies flat and the magnets meet. Those cuts are drawn as cylinders in the
tray's own frame, on the XY plane, then tilted onto the wedge with TRAY_TO_DESK and subtracted: no
sketch on the sloped face. Dimensions come from tools/concepts/concept_b_versions.py and
docs/requirements.md.
"""
import math
import traceback

import adsk.core
import adsk.fusion

# ---- dimensions (mm) --------------------------------------------------------------------------
TILT = 7.0
W, D, R = 78.0, 52.0, 6.0                   # same footprint as the tray
H_FRONT = 3.0
H_BACK = H_FRONT + D * math.tan(math.radians(TILT))     # 9.4
HOLES = [(-32, 19), (32, 19), (-32, -19), (32, -19)]    # the tray's bosses, in the tray's frame
MAGNET_R, MAGNET_DEPTH = 3.1, 1.6           # 6 x 1.5 mm disc magnet
TRAY_FEET = [(-24, -14), (24, -14), (-24, 14), (24, 14)]  # the tray's pads, in the tray's frame
PAD_D, PAD_T = 8.0, 3.0                     # silicone bumper 8 mm across, 3 mm high, on the tray and the wedge
TRAY_FOOT_DEPTH = 1.2                       # the tray's pad recess: keep in step with DS2000_Tray.py
PAD_PROUD = PAD_T - TRAY_FOOT_DEPTH         # what the tray's pads stand below its floor: 1.8 mm
SEAT_R = PAD_D / 2 + 0.3                    # wedge recess for a tray pad: 0.3 mm clearance a side (the
SEAT_DEPTH = PAD_PROUD + 0.3                #   tray is located by the magnets) and 0.3 mm deeper than the pad
FEET = [(-31, -20), (31, -20), (-31, 20), (31, 20)]     # the wedge's own pads, in its underside (desk
#                                             frame), clear in plan of the pad recesses in the top face
FOOT_R = PAD_D / 2 + 0.2                    # 0.2 mm clearance a side
FOOT_DEPTH = 0.8                            # 1.0 mm+ of wall is left under the front magnet pockets

P = adsk.core.Point3D.create
V = adsk.core.Vector3D.create
CM = 0.1                                    # Fusion's API works in cm
A = math.radians(TILT)


def tray_to_desk():
    """The tray's frame, with its floor at Z = 0, to the desk frame: the tray's front-bottom edge
    (Y = -26) lands on the wedge's front-top edge, and the tray is tilted up 7 degrees about X."""
    m = adsk.core.Matrix3D.create()
    m.setWithCoordinateSystem(P(0, (D / 2 * math.cos(A) - D / 2) * CM, (H_FRONT + D / 2 * math.sin(A)) * CM),
                              V(1, 0, 0), V(0, math.cos(A), math.sin(A)), V(0, -math.sin(A), math.cos(A)))
    return m


def circles_sketch(comp, name, centres, r):
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.name = name
    for x, y in centres:
        sk.sketchCurves.sketchCircles.addByCenterRadius(P(x * CM, y * CM, 0), r * CM)
    profs = adsk.core.ObjectCollection.create()
    for i in range(sk.profiles.count):
        profs.add(sk.profiles.item(i))
    return profs


def extrude(comp, profs, z0, z1, op):
    """Extrude the profiles from Z = z0 to Z = z1 (mm), the sketch being on the XY plane."""
    inp = comp.features.extrudeFeatures.createInput(profs, op)
    inp.startExtent = adsk.fusion.OffsetStartDefinition.create(adsk.core.ValueInput.createByReal(z0 * CM))
    inp.setDistanceExtent(False, adsk.core.ValueInput.createByReal((z1 - z0) * CM))
    return comp.features.extrudeFeatures.add(inp)


def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        if design is None:
            ui.messageBox("Open a new Fusion design first (File > New Design).")
            return
        root = design.rootComponent
        try:                                                 # an assembly design: the wedge is a component
            comp = root.occurrences.addNewComponent(adsk.core.Matrix3D.create()).component
            comp.name = "DS2000 Wedge"
        except RuntimeError:                                 # a part design has no components
            comp = root
        new, cut = adsk.fusion.FeatureOperations.NewBodyFeatureOperation, adsk.fusion.FeatureOperations.CutFeatureOperation

        # side profile on the YZ plane, extruded W across, centred on X = 0
        sk = comp.sketches.add(comp.yZConstructionPlane)
        sk.name = "Side profile"
        pts = [sk.modelToSketchSpace(P(0, y * CM, z * CM))
               for y, z in ((-D / 2, 0), (D / 2, 0), (D / 2, H_BACK), (-D / 2, H_FRONT))]
        L = sk.sketchCurves.sketchLines
        l1 = L.addByTwoPoints(pts[0], pts[1])
        l2 = L.addByTwoPoints(l1.endSketchPoint, pts[2])
        l3 = L.addByTwoPoints(l2.endSketchPoint, pts[3])
        L.addByTwoPoints(l3.endSketchPoint, l1.startSketchPoint)
        inp = comp.features.extrudeFeatures.createInput(sk.profiles.item(0), new)
        inp.setSymmetricExtent(adsk.core.ValueInput.createByReal(W * CM), True)
        body = comp.features.extrudeFeatures.add(inp).bodies.item(0)
        body.name = "Wedge"

        # round the four corners (the vertical edges at the corners) to the tray's radius
        edges = adsk.core.ObjectCollection.create()
        for e in body.edges:
            if e.geometry.curveType != adsk.core.Curve3DTypes.Line3DCurveType:
                continue
            s, t = e.geometry.startPoint, e.geometry.endPoint
            if abs(s.x - t.x) < 1e-6 and abs(s.y - t.y) < 1e-6 \
                    and abs(abs(s.x) - W / 2 * CM) < 1e-4 and abs(abs(s.y) - D / 2 * CM) < 1e-4:
                edges.add(e)
        fil = comp.features.filletFeatures.createInput()
        fil.addConstantRadiusEdgeSet(edges, adsk.core.ValueInput.createByReal(R * CM), True)
        comp.features.filletFeatures.add(fil)

        # the wedge's own pads, in its underside (Z = 0)
        extrude(comp, circles_sketch(comp, "Feet", FEET, FOOT_R), 0.0, FOOT_DEPTH, cut)

        # top face: tool cylinders in the tray's frame (floor at Z = 0, pockets going down into the
        # wedge, 1 mm of overshoot above so the cut is clean), tilted onto the wedge, then subtracted
        tools = adsk.core.ObjectCollection.create()
        for name, centres, r, depth in (("Magnet pockets", HOLES, MAGNET_R, MAGNET_DEPTH),
                                        ("Tray pad recesses", TRAY_FEET, SEAT_R, SEAT_DEPTH)):
            ext = extrude(comp, circles_sketch(comp, name, centres, r), -depth, 1.0, new)
            for i in range(ext.bodies.count):
                tools.add(ext.bodies.item(i))
        move = comp.features.moveFeatures.createInput2(tools)
        move.defineAsFreeMove(tray_to_desk())
        comp.features.moveFeatures.add(move)
        comb = comp.features.combineFeatures.createInput(body, tools)
        comb.operation = cut
        comb.isKeepToolBodies = False
        comp.features.combineFeatures.add(comb)

        app.activeViewport.fit()
    except Exception:
        if ui:
            ui.messageBox("DS2000 Wedge failed:\n{}".format(traceback.format_exc()))
