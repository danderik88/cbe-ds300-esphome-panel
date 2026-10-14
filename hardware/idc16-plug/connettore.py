# Printed male plug for the CBE DS-300 conn 17 cable (2x8 IDC female socket,
# 2.54 mm pitch). Replaces the shrouded box header of the old CBE panel.
# Run: /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd connettore.py
# Output (next to this file): spina_idc16.step/.stl
#
# Build (Dupont-housing style): crimp Dupont MALE terminals and push them in
# from the back, lance facing OUTWARDS (top row up, bottom row down). The box
# shoulder stops on the floor, the lance clicks into its window: the pin
# cannot be pushed back when mating. Release: needle in the window, press the
# lance, pull the wire. A zip tie in the two end grooves wraps over the IDC
# back: no vibration pull-out.
# Frame: z = pin axis, z=0 = floor top (mating face), shroud towards +z,
# back cavity towards -z. Key slot on the +y long wall.
import os
import FreeCAD, Part
from FreeCAD import Vector as V

OUT = os.path.dirname(os.path.abspath(__file__))

# ---- parameters (IDC socket = generic 2x8 FC-16P; MEASURE yours) ----------
PITCH = 2.54
COLS = 8
SOCKET = (25.4, 6.0)     # IDC socket body length x width
KEY_W = 5.0              # key slot width (socket bump ~4.5)
CL = 0.15                # clearance per side
SHROUD_H = 6.5           # socket insertion depth
FLOOR = 1.5              # the terminal shoulder rests under it; pins stick out ~6 - FLOOR
BACK_H = 11.0            # cavity for terminal bodies + crimp
TERM = 1.9               # Dupont male terminal box side (MEASURE); channel = TERM + 2*0.1
CATCH = 4.5              # shoulder -> lance tip: window rear edge (MEASURE, a bit more is safe)
WIN_W = 1.2              # lance window width (posts between windows = PITCH - WIN_W)
WALL_SIDE = 1.4
WALL_END = 2.6           # thicker: carries the zip-tie grooves
PIN_SLOT = 1.0           # square slot for the 0.64 mm square pin (keeps it from turning)
TIE = (3.2, 1.2)         # zip-tie groove width x depth

inner_l, inner_w = SOCKET[0] + 2 * CL, SOCKET[1] + 2 * CL
out_l, out_w = inner_l + 2 * WALL_END, inner_w + 2 * WALL_SIDE
CH = TERM + 0.2                      # square channel per terminal, like a Dupont housing
cav_w = PITCH + CH                   # outer faces of the two channel rows


def box(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


PINS = [((i - (COLS - 1) / 2) * PITCH, r * PITCH / 2) for i in range(COLS) for r in (-1, 1)]

plug = box(-out_l / 2, out_l / 2, -out_w / 2, out_w / 2, -FLOOR - BACK_H, SHROUD_H)
plug = plug.cut(box(-inner_l / 2, inner_l / 2, -inner_w / 2, inner_w / 2, 0, SHROUD_H + 1))
plug = plug.cut(box(-KEY_W / 2, KEY_W / 2, 0, out_w, 0, SHROUD_H + 1))            # key slot
for x, y in PINS:                    # channel walls: PITCH - CH (~0.44 mm, needs a 0.4 nozzle)
    plug = plug.cut(box(x - CH / 2, x + CH / 2, y - CH / 2, y + CH / 2, -FLOOR - BACK_H - 1, -FLOOR))
    plug = plug.cut(box(x - PIN_SLOT / 2, x + PIN_SLOT / 2, y - PIN_SLOT / 2, y + PIN_SLOT / 2, -FLOOR - 1, 1))
    ya, yb = (cav_w / 2 - 0.1, out_w / 2 + 1) if y > 0 else (-out_w / 2 - 1, -cav_w / 2 + 0.1)
    plug = plug.cut(box(x - WIN_W / 2, x + WIN_W / 2, ya, yb, -FLOOR - CATCH, -FLOOR - 0.3))   # lance window
for sx in (-1, 1):                                                              # zip-tie grooves
    x0 = sx * out_l / 2
    plug = plug.cut(box(min(x0, x0 - sx * TIE[1]), max(x0, x0 - sx * TIE[1]),
                        -TIE[0] / 2, TIE[0] / 2, -FLOOR - BACK_H - 1, SHROUD_H + 1))
plug = plug.removeSplitter()

# dummy IDC socket for the self-check (bump on +y, centred)
socket = box(-SOCKET[0] / 2, SOCKET[0] / 2, -SOCKET[1] / 2, SOCKET[1] / 2, 0.01, 9.0).fuse(
    box(-4.5 / 2, 4.5 / 2, SOCKET[1] / 2 - 0.01, SOCKET[1] / 2 + 0.9, 0.01, 9.0))

import MeshPart
plug.exportStep(os.path.join(OUT, "spina_idc16.step"))
MeshPart.meshFromShape(Shape=plug, LinearDeflection=0.02, AngularDeflection=0.2).write(
    os.path.join(OUT, "spina_idc16.stl"))
ok = plug.isValid() and len(plug.Solids) == 1
fit = plug.common(socket).Volume
flipped = socket.copy(); flipped.rotate(V(0, 0, 0), V(0, 0, 1), 180)
wrong = plug.common(flipped).Volume
print("valid=%s solids=%d  %.0f x %.1f x %.1f mm  vol=%.1f cm3" % (
    plug.isValid(), len(plug.Solids), out_l, out_w, FLOOR + BACK_H + SHROUD_H, plug.Volume / 1000))
print("IDC nel verso giusto: interferenza=%.2f (deve essere 0)" % fit)
print("IDC girato 180: interferenza=%.2f (deve essere >0 = non entra)" % wrong)
print("pin sporgenti ~%.1f mm con pin Dupont da 6 mm" % (6 - FLOOR))
ok &= fit < 0.01 and wrong > 0.5
print("OK" if ok else "FALLITO")
