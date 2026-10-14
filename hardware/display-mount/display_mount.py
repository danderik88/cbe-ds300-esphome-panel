# Wall mount for the Guition JC8012P4A1C (10.1") in the camper.
# Run: /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd display_mount.py
# Output (next to this file): display_plate.step/.stl, wall_bracket.step/.stl,
# assembly.step (with a dummy display, for checking).
#
# Two printed parts:
#  - display plate: screwed to the 6 M2.5 bosses of the display,
#    carries two French-cleat hooks at the top and a lock lug at the bottom.
#  - wall bracket: flat base covering the old panel hole (210x75),
#    two wedge towers with the mating cleats (10 deg tilt, top away from wall),
#    two bottom pads and a lock block. One M3 screw from below goes through the
#    lock block into a heat-set insert in the plate lug: the display cannot lift
#    off the cleats until that screw is removed.
#
# Frames: "F-local" = plate frame (x right, y up along the plate, z towards the
# viewer, z=0 = plate back face). Global = wall frame (Z=0 wall surface).
# Display dimensions from the official Guition drawing (3-Structure_Diagram/
# JC8012P4A1.pdf); landscape, FPC/camera end on the LEFT (-x).
import math, os
import FreeCAD, Part
from FreeCAD import Vector as V

OUT = os.path.dirname(os.path.abspath(__file__))

# ---- parameters ------------------------------------------------------------
TILT = 10.0          # deg, top edge away from the wall
CL = 0.2             # printing clearance on every sliding/mating face
T_PLATE = 6.0        # display plate thickness
D_CLEAT = 8.0        # cleat depth (towards the wall)
Y0 = 58.0            # cleat 45 deg interface height (F-local y at the tower face)
W0 = 12.0            # distance wall -> plate back at the plate bottom edge
T_BASE = 4.0         # wall base thickness
WALL_HOLE = (210.0, 75.0)   # old CBE panel cut-out (covered by the base)

# display (official drawing)
DISP_L, DISP_W, DISP_T = 242.8, 158.7, 7.0
BOSS_H, BOSS_D = 4.5, 7.5
HOUSING = (138.35, 93.5, 15.51)      # rear shell, protrudes 15.51 from frame back
HOUSING_DX = -0.73                   # housing centre offset towards the FPC end
# middle holes: on the real display they sit on the half WITHOUT the FPC block
# (the Guition drawing shows them on the FPC half: checked on the part, it's wrong)
HOLES = [(x, y) for x in (-106.4, 16.4, 106.4) for y in (-64.35, 64.35)]

PLATE_X = 116.0
PLATE_Y = (-73.0, 76.0)           # top kept below the display top edge
CLEAT_X = (76.0, 114.0)              # |x| range of the two cleats
LOCK_X = (32.0, 48.0)                # lock lug / block, off-centre (edge connector notch at x~0)
LOCK_SCREW_Z = -3.0

rot = FreeCAD.Rotation(V(1, 0, 0), TILT)
s, c = math.sin(math.radians(TILT)), math.cos(math.radians(TILT))
W_C = W0 - PLATE_Y[0] * s            # global Z of the F-local origin
PL = FreeCAD.Placement(V(0, 0, W_C), rot)


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def prism_yz(pts, x0, x1):
    """Polygon in the (y, z) plane extruded along x."""
    w = Part.makePolygon([V(x0, y, z) for y, z in pts] + [V(x0, pts[0][0], pts[0][1])])
    return Part.Face(w).extrude(V(x1 - x0, 0, 0))


def cyl_y(x, z, y0, y1, d):
    return Part.makeCylinder(d / 2, y1 - y0, V(x, y0, z), V(0, 1, 0))


def cyl_z(x, y, z0, z1, d):
    return Part.makeCylinder(d / 2, z1 - z0, V(x, y, z0), V(0, 0, 1))


def both_sides(x0, x1):
    return [(x0, x1), (-x1, -x0)]


# ---- display plate (F-local) -----------------------------------------------
plate = box(-PLATE_X, PLATE_X, PLATE_Y[0], PLATE_Y[1], 0, T_PLATE)
hx, hy = HOUSING[0] / 2 + 1.0, HOUSING[1] / 2 + 1.0
plate = plate.cut(box(HOUSING_DX - hx, HOUSING_DX + hx, -hy, hy, -1, T_PLATE + 1))
# FPC/camera block + ribbons on the back of the display (left end)
plate = plate.cut(box(-PLATE_X - 5, -69.0, -27.5, 27.5, -1, T_PLATE + 1))
# edge connector/cable at the middle of a long edge: notch both edges,
# so the display can be mounted either way up
for ya, yb in ((60.0, PLATE_Y[1] + 1), (PLATE_Y[0] - 1, -60.0)):
    plate = plate.cut(box(-9.0, 10.0, ya, yb, -1, T_PLATE + 1))
# cleat hooks (behind the plate)
for xa, xb in both_sides(*CLEAT_X):
    plate = plate.fuse(prism_yz([(Y0 + CL * math.sqrt(2) + CL, -D_CLEAT + CL),
                                 (PLATE_Y[1], -D_CLEAT + CL), (PLATE_Y[1], 0.0),
                                 (Y0 + D_CLEAT + CL * math.sqrt(2), 0.0)], xa, xb))
# lock lug with heat-set insert hole (M3, drilled from below)
plate = plate.fuse(box(LOCK_X[0], LOCK_X[1], PLATE_Y[0], PLATE_Y[0] + 12, -D_CLEAT + CL, 0))
plate = plate.cut(cyl_y(sum(LOCK_X) / 2, LOCK_SCREW_Z, PLATE_Y[0] - 1, PLATE_Y[0] + 7, 4.1))
# M2.5 holes; heads on the wall side, 3.5 mm of plate under the head
for x, y in HOLES:
    plate = plate.cut(cyl_z(x, y, -1, T_PLATE + 1, 2.9))
    plate = plate.cut(cyl_z(x, y, -40, T_PLATE - 3.5, 5.6))
plate = plate.removeSplitter()

# ---- wall bracket ----------------------------------------------------------
BACK = -80.0   # towers are built long towards the wall, then trimmed at Z=0
parts = []
for xa, xb in both_sides(*CLEAT_X):
    parts.append(prism_yz([(PLATE_Y[0], BACK), (PLATE_Y[0], -CL), (Y0 + D_CLEAT - CL, -CL),
                           (Y0, -D_CLEAT), (PLATE_Y[1], -D_CLEAT), (PLATE_Y[1], BACK)], xa, xb))
lock = box(LOCK_X[0], LOCK_X[1], PLATE_Y[0] - 6.2, PLATE_Y[0] - CL, BACK, -CL)
lock = lock.cut(cyl_y(sum(LOCK_X) / 2, LOCK_SCREW_Z, PLATE_Y[0] - 10, PLATE_Y[0] + 1, 3.4))
parts.append(lock)
towers = parts[0].fuse(parts[1:])
for x, y in HOLES:                   # relief for the M2.5 heads under the plate
    towers = towers.cut(cyl_z(x, y, -2.5, 1, 7.0))
towers.Placement = PL
towers = towers.common(box(-200, 200, -200, 200, 0, 200))   # trim at the wall

BRACKET_Y = (-80.0, 76.5)            # global; hidden behind the tilted display
towers = towers.common(box(-200, 200, BRACKET_Y[0], BRACKET_Y[1], 0, 200))
base = box(-PLATE_X, PLATE_X, BRACKET_Y[0], BRACKET_Y[1], 0, T_BASE)
base = base.makeFillet(10.0, [e for e in base.Edges if abs(e.Vertexes[0].Z - e.Vertexes[1].Z) > 1])
base = base.makeChamfer(1.5, [e for e in base.Edges if all(abs(v.Z - T_BASE) < 1e-6 for v in e.Vertexes)])
base = base.cut(box(-50, 50, -22, 22, -1, T_BASE + 1))       # cable window, hidden by the housing
for x in (-60.0, 60.0):
    for y in (-62.0, 62.0):
        base = base.cut(cyl_z(x, y, -1, T_BASE + 1, 4.2))
        base = base.cut(Part.makeCone(2.1, 4.5, 2.4, V(x, y, T_BASE - 2.4)))
bracket = base.fuse(towers).removeSplitter()

# ---- dummy display for checks (F-local) --------------------------------------
zf = T_PLATE + BOSS_H
disp = box(-DISP_L / 2, DISP_L / 2, -DISP_W / 2, DISP_W / 2, zf, zf + DISP_T)
disp = disp.fuse(box(HOUSING_DX - HOUSING[0] / 2, HOUSING_DX + HOUSING[0] / 2,
                     -HOUSING[1] / 2, HOUSING[1] / 2, zf - HOUSING[2], zf))
disp = disp.fuse(box(-118.4, -96.2, -26.0, 26.0, zf - BOSS_H + 0.1, zf))   # FPC block (height assumed)
for x, y in HOLES:
    disp = disp.fuse(cyl_z(x, y, T_PLATE, zf, BOSS_D).cut(cyl_z(x, y, T_PLATE, zf, 2.5)))

plate_g = plate.copy(); plate_g.Placement = PL
disp_g = disp.copy(); disp_g.Placement = PL

import MeshPart
for name, shp in (("display_plate", plate), ("wall_bracket", bracket)):
    shp.exportStep(os.path.join(OUT, name + ".step"))
    MeshPart.meshFromShape(Shape=shp, LinearDeflection=0.05, AngularDeflection=0.2).write(os.path.join(OUT, name + ".stl"))
Part.makeCompound([plate_g, bracket, disp_g]).exportStep(os.path.join(OUT, "assembly.step"))
