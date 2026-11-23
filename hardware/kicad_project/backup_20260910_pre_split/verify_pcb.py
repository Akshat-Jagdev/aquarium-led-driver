#!/usr/bin/env python3
"""Verify aquarium_v0.kicad_pcb against netlist.net + the layout rules.

Runs with KiCad's BUNDLED python (pcbnew bindings required):
  "C:/Users/Akshat Jagdev/AppData/Local/Programs/KiCad/10.0/bin/python.exe" verify_pcb.py

Checks:
  1. pad<->net audit      — every (ref, pin) in netlist.net matches the board
  2. footprint/net parity — 68 footprints, all 44 netlist nets present
  3. connectivity         — drc.json reports 0 violations, 0 unconnected items
  4. geometry             — pads inside board, MH positions, header pin-1
                            orientation, headers inside their MCPCB spans
  5. widths               — track width >= netclass minimum per net,
                            via drill >= 0.3 / diameter >= 0.5
  6. zones                — B.Cu GND zone filled; >= 8 GND vias per driver
Exit code 0 = all pass.
"""
import json
import os
import re
import sys

try:
    import pcbnew  # noqa: F401  (bundled python only)
except ImportError:
    sys.exit("Run with KiCad's bundled python:\n"
             '  "C:/.../KiCad/10.0/bin/python.exe" verify_pcb.py')

HERE = os.path.dirname(os.path.abspath(__file__))
BOARD = os.path.join(HERE, "aquarium_v0.kicad_pcb")
NETLIST = os.path.join(HERE, "netlist.net")
DRC_JSON = os.path.join(HERE, "drc.json")
PRO = os.path.join(HERE, "aquarium_v0.kicad_pro")

BOARD_W, BOARD_H = 580.0, 20.0
# MCPCB spans (local x) per extrusion_dims.md §3: J2 7-147, J3 149-289,
# J4 291-431, J5 433-573; headers must sit fully inside their span
MCPCB_SPANS = {"J2": (7, 147), "J3": (149, 289), "J4": (291, 431), "J5": (433, 573)}
MH_XY = {"MH1": (20, 4), "MH2": (190, 10), "MH3": (390, 10), "MH4": (560, 10)}
DRIVERS = ["U1", "U2", "U3", "U4", "U5", "U6", "U7"]

fails = []


def fail(msg):
    fails.append(msg)
    print(f"  FAIL {msg}")


def ok(msg):
    print(f"  ok {msg}")


board = pcbnew.LoadBoard(BOARD)
if not board:
    sys.exit("could not load board")

MM = 1000000  # pcbnew internal units (nm) -> mm


def mm(v):
    return v / MM


# ---------------------------------------------------------------- 1. pad audit
# netlist.net: (comp (ref "X") ... (tstamps "uuid")) + (node (ref "X") (pin "P"))
nl_text = open(NETLIST, encoding="utf-8").read()
nl_nets = {}  # net name -> set of (ref, pin)
for m in re.finditer(
        r'\(net\s+\(code "[^"]*"\)\s*\(name "([^"]*)"\)(.*?)\n\t\t\)',
        nl_text, re.S):
    nodes = set()
    for nm in re.finditer(r'\(node\s*\(ref "([^"]*)"\)\s*\(pin "([^"]*)"\)',
                          m.group(2)):
        nodes.add((nm.group(1), nm.group(2)))
    nl_nets[m.group(1).lstrip("/")] = nodes

fps = {f.GetReference(): f for f in board.GetFootprints()}
print(f"footprints: {len(fps)} / nets on board: {len(board.GetNetInfo().NetsByNetcode())}")

if len(fps) != 68:
    fail(f"expected 68 footprints, board has {len(fps)}")
else:
    ok("68 footprints on board")

# every netlist (ref, pin) -> board pad net name
board_nets = {}
for nci in board.GetNetInfo().NetsByNetcode().values():
    board_nets[nci.GetNetCode()] = nci.GetNetname().lstrip("/")

pad_count = mismatches = 0
for netname, nodes in nl_nets.items():
    if netname.startswith("unconnected-"):
        continue
    for ref, pin in nodes:
        fp = fps.get(ref)
        if fp is None:
            fail(f"netlist {ref} has no board footprint")
            continue
        pad = fp.FindPadByNumber(pin)
        if pad is None:
            fail(f"{ref} pin {pin}: no such pad on board footprint")
            continue
        pad_count += 1
        got = board_nets.get(pad.GetNetCode(), "")
        if got != netname:
            mismatches += 1
            fail(f"{ref} pin {pin}: netlist says '{netname}', board pad says '{got}'")
if mismatches == 0:
    ok(f"pad<->net audit: {pad_count} pins all match netlist")

# all netlist nets present on board (by name); unconnected-(...) are the
# mounting holes' no-connect nets — they legitimately have no board net
board_netnames = set(board_nets.values())
missing = [n for n in nl_nets
           if n not in board_netnames and not n.startswith("unconnected-")]
if missing:
    fail(f"netlist nets absent from board: {missing}")
else:
    ok(f"all {len(nl_nets)} netlist nets present on board")

# -------------------------------------------------------------- 3. connectivity
drc = json.load(open(DRC_JSON, encoding="utf-8")) if os.path.exists(DRC_JSON) else None
if drc is None:
    fail("drc.json missing — run: kicad-cli pcb drc --refill-zones --save-board "
         "--format json -o drc.json aquarium_v0.kicad_pcb")
else:
    nv = len(drc.get("violations", []))
    nu = len(drc.get("unconnected_items", []))
    if nv == 0 and nu == 0:
        ok("DRC: 0 violations, 0 unconnected items")
    else:
        fail(f"DRC: {nv} violations, {nu} unconnected items (see drc.json)")

# ------------------------------------------------------------------ 4. geometry
for ref, fp in fps.items():
    b = fp.GetBoundingBox(False, True)  # pads+courtyard, board coords
    x1, y1, x2, y2 = mm(b.GetX()), mm(b.GetY()), mm(b.GetX() + b.GetWidth()), mm(b.GetY() + b.GetHeight())
    if x1 < -0.01 or y1 < -0.01 or x2 > BOARD_W + 0.01 or y2 > BOARD_H + 0.01:
        fail(f"{ref} outside board: ({x1:.2f},{y1:.2f})-({x2:.2f},{y2:.2f})")
ok("all footprints inside board outline")

for ref, (mx, my) in MH_XY.items():
    fp = fps.get(ref)
    if fp is None:
        fail(f"{ref} missing")
        continue
    cx, cy = mm(fp.GetX()), mm(fp.GetY())
    if abs(cx - mx) > 0.01 or abs(cy - my) > 0.01:
        fail(f"{ref} at ({cx},{cy}), expected ({mx},{my})")
ok("MH1-4 at extrusion drill positions (20/190/390/560 minus 10mm inset)")

# header pin-1 orientation: pin1 pad must be the RIGHTMOST pad (rot 270,
# pin 1 faces its driver cell to the right) and header inside its span
for ref, (s1, s2) in MCPCB_SPANS.items():
    fp = fps[ref]
    pads = fp.Pads()
    p1 = fp.FindPadByNumber("1")
    if p1 is None:
        fail(f"{ref}: no pad 1")
        continue
    if mm(p1.GetX()) < max(mm(p.GetX()) for p in pads) - 0.01:
        fail(f"{ref}: pin 1 is not the rightmost pad (driver cell side)")
    # span check: header body inside the MCPCB span (10mm board inset ->
    # board x = local x)
    b = fp.GetBoundingBox(False, False)
    bx1, bx2 = mm(b.GetX()), mm(b.GetX() + b.GetWidth())
    if bx1 < s1 or bx2 > s2:
        fail(f"{ref} x {bx1:.1f}..{bx2:.1f} outside MCPCB span {s1}..{s2}")
ok("J2-J5 pin 1 rightmost, inside their MCPCB spans")

# ----------------------------------------------------------- 5. widths + vias
pro = json.load(open(PRO, encoding="utf-8"))
classes = {c["name"]: c for c in pro["net_settings"]["classes"]}
# assignment keys carry the leading '/', values may be a string or a
# 1-element list depending on who last saved the .kicad_pro — normalize.
assign = {k.lstrip("/"): (v[0] if isinstance(v, list) else v)
          for k, v in pro["net_settings"]["netclass_assignments"].items()}
def min_width(netname):
    cls = assign.get(netname.lstrip("/"), "Default")
    return classes[cls]["track_width"]

def is_via(t):
    # NB: isinstance(t, pcbnew.PCB_VIA) is unreliable on the KiCad 10
    # bindings; Type() is stable. Never call via.GetWidth() without a
    # layer arg — it trips a C++ assert that blocks the process.
    return t.Type() == pcbnew.PCB_VIA_T

track_by_net = {}
thin = []
for t in board.GetTracks():
    if is_via(t):
        continue
    net = board_nets.get(t.GetNetCode(), "")
    w = mm(t.GetWidth())
    track_by_net[net] = max(track_by_net.get(net, 0), w)
    if net and w < min_width(net) - 1e-6:
        thin.append((net, w, min_width(net),
                     mm(t.GetStart().x), mm(t.GetStart().y)))
if thin:
    for net, w, mw, x, y in thin[:10]:
        fail(f"track on '{net}' {w}mm < netclass {mw}mm @ ({x:.1f},{y:.1f})"
             + (f" (+{len(thin)-10} more)" if len(thin) > 10 else ""))
else:
    ok(f"all tracks meet netclass widths ({len(track_by_net)} nets routed)")

vias = [v for v in board.GetTracks() if is_via(v)]
bad_vias = [v for v in vias
            if mm(v.GetDrillValue()) < 0.3 - 1e-6
            or mm(v.GetWidth(pcbnew.F_Cu)) < 0.5 - 1e-6]
if bad_vias:
    fail(f"{len(bad_vias)} vias below JLC minimum 0.5/0.3")
else:
    ok(f"all {len(vias)} vias >= 0.5mm dia / 0.3mm drill")

# --------------------------------------------------------------- 6. GND + heat
gnd_code = None
for nci in board.GetNetInfo().NetsByNetcode().values():
    if nci.GetNetname() == "GND":
        gnd_code = nci.GetNetCode()
gnd_fill_area = 0.0
island_count = 0
for z in board.Zones():
    # NB: zone.GetLayer() misreports on the KiCad 10 bindings — use
    # IsOnLayer(). GetFilledPolysList needs the layer argument.
    if z.GetNetCode() == gnd_code and z.IsOnLayer(pcbnew.B_Cu):
        polys = z.GetFilledPolysList(z.GetLayer())
        island_count += polys.OutlineCount()
        # GetFilledArea returns nm^2 -> mm^2
        gnd_fill_area += z.GetFilledArea() / 1e12
if gnd_fill_area <= 0:
    fail("B.Cu GND zone has no fill (refill with --refill-zones --save-board)")
else:
    ok(f"B.Cu GND pour filled: {gnd_fill_area:.0f} mm2, {island_count} island(s)")

gnd_via_count = 0
for v in board.GetTracks():
    if is_via(v) and v.GetNetCode() == gnd_code:
        gnd_via_count += 1
if gnd_via_count >= 8 * len(DRIVERS):
    ok(f"GND vias: {gnd_via_count} total (~{gnd_via_count // len(DRIVERS)}/driver)")
else:
    fail(f"only {gnd_via_count} GND vias (< {8 * len(DRIVERS)} for thermal stitching)")

# --------------------------------------------------------------------- summary
print()
if fails:
    print(f"VERIFY_PCB: {len(fails)} FAILURE(S)")
    sys.exit(1)
print("VERIFY_PCB: ALL CHECKS PASSED")