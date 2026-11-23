#!/usr/bin/env python3
"""Verify one split board against netlist.net + the layout rules.

Runs with KiCad's BUNDLED python (pcbnew bindings required):
  "C:/Users/Akshat Jagdev/AppData/Local/Programs/KiCad/10.0/bin/python.exe" \
      verify_pcb.py --board 4

The 4-board split keeps the original absolute coordinates, so all x
positions below are in the original 580 mm frame. Checks:
  1. footprint set         — exact per-board ref inventory (78 parts total)
  2. pad<->net audit       — every (ref, pin) on this board matches netlist
                             both ways; all board nets exist in netlist
  3. connectivity         — drc_board{N}.json reports 0 violations,
                             0 unconnected items
  4. geometry             — footprints inside this board's Edge.Cuts,
                             MH positions, J2-J5 pin-1 rightmost + MCPCB
                             span, joint headers pin-1 rightmost
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
             '  "C:/.../KiCad/10.0/bin/python.exe" verify_pcb.py --board N')

# ------------------------------------------------------------ --board N arg
if "--board" not in sys.argv:
    sys.exit("usage: verify_pcb.py --board N   (N = 1..4)")
try:
    N = int(sys.argv[sys.argv.index("--board") + 1])
except (IndexError, ValueError):
    sys.exit("usage: verify_pcb.py --board N   (N = 1..4)")
if N not in (1, 2, 3, 4):
    sys.exit(f"bad board {N}: expected 1..4")

HERE = os.path.dirname(os.path.abspath(__file__))
BOARD = os.path.join(HERE, f"aquarium_v0_board{N}.kicad_pcb")
NETLIST = os.path.join(HERE, "netlist.net")
DRC_JSON = os.path.join(HERE, f"drc_board{N}.json")
PRO = os.path.join(HERE, f"aquarium_v0_board{N}.kicad_pro")

# per-board inventory (ref sets are exact; union = 78 parts)
EXPECTED_REFS = {
    1: ["C1", "C10", "C2", "C20", "C3", "C4", "D1", "F1", "J1", "J2",
        "J6", "J7", "J8", "L1", "MH1", "MH5", "R1", "R10", "R2", "R3",
        "R4", "R5", "R6", "R7", "R8", "U1", "U8", "U9"],
    2: ["C11", "C14", "C15", "C21", "C24", "C25", "D2", "D5", "D6",
        "J10", "J3", "J9", "L2", "L5", "L6", "MH2", "MH6", "R11", "R14",
        "R15", "U2", "U5", "U6"],
    3: ["C12", "C22", "D3", "J11", "J12", "J4", "L3", "MH3", "MH7",
        "R12", "U3"],
    4: ["C13", "C16", "C23", "C26", "D4", "D7", "J13", "J5", "L4", "L7",
        "MH4", "MH8", "R13", "R16", "U4", "U7"],
}
# mounting holes per board (absolute coords, original frame)
MH_XY = {
    1: {"MH1": (20, 4), "MH5": (112, 11)},
    2: {"MH2": (190, 10), "MH6": (290, 10)},
    3: {"MH3": (390, 10), "MH7": (330, 4.8)},
    4: {"MH4": (560, 10), "MH8": (495, 4.8)},
}
# LED driver cells per board
DRIVERS = {
    1: ["U1"],
    2: ["U2", "U5", "U6"],
    3: ["U3"],
    4: ["U4", "U7"],
}
# MCPCB spans (absolute x, per extrusion_dims.md §3) for the J2-J5
# connector of this board; headers must sit fully inside their span
MCPCB_SPANS = {"J2": (7, 147), "J3": (149, 289), "J4": (291, 431),
               "J5": (433, 573)}
BOARD_J25 = {1: "J2", 2: "J3", 3: "J4", 4: "J5"}[N]
JOINT_HEADERS = {1: ["J8"], 2: ["J9", "J10"], 3: ["J11", "J12"],
                 4: ["J13"]}[N]

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


# ---------------------------------------------------------------- 1. footprints
fps = {f.GetReference(): f for f in board.GetFootprints()}
print(f"board {N}: footprints {len(fps)} / "
      f"nets on board {len(board.GetNetInfo().NetsByNetcode())}")

expected = set(EXPECTED_REFS[N])
if set(fps) != expected:
    miss = sorted(expected - set(fps))
    extra = sorted(set(fps) - expected)
    fail(f"footprint set mismatch: missing {miss}, unexpected {extra}")
else:
    ok(f"footprint set exact: {len(expected)} refs match inventory")

# ---------------------------------------------------------------- 2. pad audit
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

board_nets = {}
for nci in board.GetNetInfo().NetsByNetcode().values():
    board_nets[nci.GetNetCode()] = nci.GetNetname().lstrip("/")

# netlist -> board, restricted to this board's refs
pad_count = mismatches = 0
for netname, nodes in nl_nets.items():
    if netname.startswith("unconnected-"):
        continue
    for ref, pin in nodes:
        if ref not in fps:
            continue  # lives on another board
        fp = fps[ref]
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
    ok(f"pad<->net audit: {pad_count} on-board pins all match netlist")

# board -> netlist: every on-board pad with a real net must appear in the
# netlist with the same net name (catches stale board nets)
nl_pinmap = {}  # (ref, pin) -> netname
for netname, nodes in nl_nets.items():
    for ref, pin in nodes:
        nl_pinmap[(ref, pin)] = netname
rev_bad = 0
for ref, fp in fps.items():
    for pad in fp.Pads():
        got = board_nets.get(pad.GetNetCode(), "")
        if not got or got.startswith("unconnected-"):
            continue  # MH no-connect pads
        want = nl_pinmap.get((ref, pad.GetPadName()))
        if want != got:
            rev_bad += 1
            fail(f"{ref} pin {pad.GetPadName()}: board says '{got}', "
                 f"netlist says '{want}'")
if rev_bad == 0:
    ok("reverse audit: every on-board pad net matches netlist")

# all real nets used on this board exist in the netlist
board_netnames = set(board_nets.values())
nl_netnames = set(nl_nets)
missing = [n for n in board_netnames
           if n and not n.startswith("unconnected-") and n not in nl_netnames]
if missing:
    fail(f"board nets absent from netlist: {sorted(missing)}")
else:
    ok("all board nets present in netlist")

# -------------------------------------------------------------- 3. connectivity
drc = json.load(open(DRC_JSON, encoding="utf-8")) if os.path.exists(DRC_JSON) else None
if drc is None:
    fail(f"{os.path.basename(DRC_JSON)} missing — run: kicad-cli pcb drc "
         "--refill-zones --save-board --format json "
         f"-o {os.path.basename(DRC_JSON)} aquarium_v0_board{N}.kicad_pcb")
else:
    nv = len(drc.get("violations", []))
    nu = len(drc.get("unconnected_items", []))
    if nv == 0 and nu == 0:
        ok("DRC: 0 violations, 0 unconnected items")
    else:
        fail(f"DRC: {nv} violations, {nu} unconnected items")

# ------------------------------------------------------------------ 4. geometry
bb = board.GetBoardEdgesBoundingBox()
bx1, by1 = mm(bb.GetX()), mm(bb.GetY())
bx2, by2 = mm(bb.GetX() + bb.GetWidth()), mm(bb.GetY() + bb.GetHeight())
ok(f"board {N} outline: x {bx1:.1f}..{bx2:.1f}, y {by1:.1f}..{by2:.1f}")

def copper_bbox_mm(fp):
    """Union of pad bboxes (mm) — copper footprint only.

    The courtyard bbox is NOT used: the joint headers sit at the board
    edge and their courtyards overhang by ~0.3 mm, which is documentation,
    not copper (DRC's edge-clearance check gates the real copper).
    """
    x1 = y1 = float("inf")
    x2 = y2 = float("-inf")
    for pad in fp.Pads():
        b = pad.GetBoundingBox()  # accounts for shape + rotation
        x1 = min(x1, mm(b.GetX()))
        y1 = min(y1, mm(b.GetY()))
        x2 = max(x2, mm(b.GetX() + b.GetWidth()))
        y2 = max(y2, mm(b.GetY() + b.GetHeight()))
    return x1, y1, x2, y2


for ref, fp in fps.items():
    x1, y1, x2, y2 = copper_bbox_mm(fp)
    if x1 < bx1 - 0.01 or y1 < by1 - 0.01 or x2 > bx2 + 0.01 or y2 > by2 + 0.01:
        fail(f"{ref} copper outside board: ({x1:.2f},{y1:.2f})-({x2:.2f},{y2:.2f})")
ok("all footprint copper inside board outline")

for ref, (mx, my) in MH_XY[N].items():
    fp = fps.get(ref)
    if fp is None:
        fail(f"{ref} missing")
        continue
    cx, cy = mm(fp.GetX()), mm(fp.GetY())
    if abs(cx - mx) > 0.01 or abs(cy - my) > 0.01:
        fail(f"{ref} at ({cx},{cy}), expected ({mx},{my})")
ok(f"board {N} mounting holes at their drill positions")

# header pin-1 orientation: pin1 pad must be the RIGHTMOST pad (rot 270,
# pin 1 faces its driver cell to the right) and header inside its span
for ref, span in [(BOARD_J25, MCPCB_SPANS[BOARD_J25])]:
    fp = fps.get(ref)
    if fp is None:
        fail(f"{ref} missing")
        continue
    pads = fp.Pads()
    p1 = fp.FindPadByNumber("1")
    if p1 is None:
        fail(f"{ref}: no pad 1")
        continue
    if mm(p1.GetX()) < max(mm(p.GetX()) for p in pads) - 0.01:
        fail(f"{ref}: pin 1 is not the rightmost pad (driver cell side)")
        continue
    # span check: header body inside the MCPCB span (10mm board inset ->
    # board x = local x)
    b = fp.GetBoundingBox(False, False)
    hx1, hx2 = mm(b.GetX()), mm(b.GetX() + b.GetWidth())
    if hx1 < span[0] or hx2 > span[1]:
        fail(f"{ref} x {hx1:.1f}..{hx2:.1f} outside MCPCB span {span[0]}..{span[1]}")
    else:
        ok(f"{ref} pin 1 rightmost, inside its MCPCB span")

# joint headers (J8-J13): pin 1 rightmost, body inside this board
for ref in JOINT_HEADERS:
    fp = fps.get(ref)
    if fp is None:
        fail(f"{ref} missing")
        continue
    pads = fp.Pads()
    p1 = fp.FindPadByNumber("1")
    if p1 is None or mm(p1.GetX()) < max(mm(p.GetX()) for p in pads) - 0.01:
        fail(f"{ref}: pin 1 is not the rightmost pad")
        continue
    b = fp.GetBoundingBox(False, False)
    hx1, hx2 = mm(b.GetX()), mm(b.GetX() + b.GetWidth())
    if hx1 < bx1 - 0.01 or hx2 > bx2 + 0.01:
        fail(f"{ref} x {hx1:.1f}..{hx2:.1f} outside board outline")
    else:
        ok(f"{ref} pin 1 rightmost, inside board outline")

# ----------------------------------------------------------- 5. widths + vias
pro = json.load(open(PRO, encoding="utf-8"))
classes = {c["name"]: c for c in pro["net_settings"]["classes"]}
# assignment keys carry the leading '/', values may be a string or a
# 1-element list depending on who last saved the .kicad_pro — normalize.
assign = {k.lstrip("/"): (v[0] if isinstance(v, list) else v)
          for k, v in (pro["net_settings"].get("netclass_assignments")
                       or {}).items()}


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
need = 8 * len(DRIVERS[N])
if gnd_via_count >= need:
    ok(f"GND vias: {gnd_via_count} total "
       f"(~{gnd_via_count // len(DRIVERS[N])}/driver, {len(DRIVERS[N])} driver(s) on board {N})")
else:
    fail(f"only {gnd_via_count} GND vias (< {need} for thermal stitching)")

# --------------------------------------------------------------------- summary
print()
if fails:
    print(f"VERIFY_PCB board {N}: {len(fails)} FAILURE(S)")
    sys.exit(1)
print(f"VERIFY_PCB board {N}: ALL PASS")