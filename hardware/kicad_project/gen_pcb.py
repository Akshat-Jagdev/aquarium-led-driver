#!/usr/bin/env python3
"""
Generate the ColorBoost V0 driver-strip PCBs (KiCad 10 .kicad_pcb).

4-BOARD SPLIT (2026-09-10): the 580x20 strip is cut into 4 fab-friendly
boards joined off-board by pin-header harnesses (J8-J13). All part
coordinates stay in the ORIGINAL 580-frame; each board file gets only the
footprints whose placement anchor falls in its x-window, its own Edge.Cuts
rect, zones, silk, and overlay routes (ROUTES_EXTRA.json routes/vias are
filtered by window: anything crossing a seam is intentionally dropped —
those nets now travel through the joint headers).

Deterministic layout in the same spirit as gen_schematic.py: netlist.net is
the single source of truth for pad->net; footprint geometry is embedded
verbatim from the KiCad 10 .pretty libraries; all coordinates are data
tables. Self-asserts the critical placement rules from
hardware/mechanical/pcb_layout_notes.md before writing each file.

Board windows (absolute x, mm — gaps are the assembly seams):
  B1 [0, 150.5]    logic cluster + U1/W1 cell + J2 + J8     (~1.6 A at seam 1)
  B2 [151, 300]    U5/R + U6/B + U2/W2 cells + J3 + J9/J10
  B3 [300.5, 398.4] U3/W3 cell + J4 + J11/J12
  B4 [398.9, 574]  U7/DR + U4/W4 cells + J5 + J13

Run:  python gen_pcb.py [--board N]   (KiCad GUI must be closed)
Out:  aquarium_v0_board{N}.kicad_pcb + .kicad_pro, N = 1..4

Then: kicad-cli pcb drc --refill-zones --save-board --exit-code-violations
       --format json -o drc.json aquarium_v0_board{N}.kicad_pcb
"""
import json
import math
import os
import re
import sys
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
NET_PATH = os.path.join(HERE, "netlist.net")
PRO_TEMPLATE = os.path.join(HERE, "aquarium_v0.kicad_pro")  # from gen_schematic
if sys.platform == "darwin":
    FP_ROOT = ("/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints")
else:
    FP_ROOT = (r"C:\Users\Akshat Jagdev\AppData\Local\Programs\KiCad\10.0"
               r"\share\kicad\footprints")

# (number, x0, x1) — seam gaps: 150.5-151, 300-300.5, 398.4-398.9
BOARDS = [(1, 0.0, 150.5), (2, 151.0, 300.0),
          (3, 300.5, 398.4), (4, 398.9, 574.0)]
BOARD_H = 20.0    # mm, channel usable interior is 40 mm (20 MCPCB + 20 strip)
EDGE_CLEAR = 0.3  # copper-to-edge keepout


def U():
    # Deterministic uuid5 from a counter (not uuid4): kicad-cli's
    # --save-board re-orders items by uuid, so random uuids would make
    # two regens of identical sources differ in file order. With uuid5
    # the whole gen -> DRC-refill pipeline is byte-reproducible.
    U.n += 1
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"aquarium-v0-{U.n}"))


U.n = 0


out = []


def L(indent, text):
    out.append("\t" * indent + text)


def fmt(v):
    """KiCad mm coordinate: 4 decimals, no trailing zeros."""
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return s if s not in ("-0", "") else "0"


# ------------------------------------------------------------ netlist parse

def parse_netlist(path):
    """-> nets {name: code}, comps {ref: {value, footprint, pins, tstamp}}

    KiCad 10 netlist: tab-indented s-expr; comps have (ref)/(value)/
    (footprint)/(tstamps) each on its own line inside (comp ...) blocks;
    nodes live inside (net ...) blocks."""
    text = open(path, encoding="utf-8").read()
    nets = {}
    for m in re.finditer(
            r'\(net\s+\(code "([^"]*)"\)\s*\(name "([^"]*)"\)(.*?)\n\t\t\)',
            text, re.S):
        nets[m.group(2)] = int(m.group(1))
    comps = {}
    for m in re.finditer(r'\(comp\s*\n(.*?)\n\t\t\)', text, re.S):
        body = m.group(1)
        def grab(tag):
            mm = re.search(r'\(' + tag + r' "([^"]*)"\)', body)
            return mm.group(1) if mm else None
        def grab_last(tag):
            # sheetpath carries its own (tstamps "/") BEFORE the comp-level
            # (tstamps "uuid") — the symbol uuid is the last occurrence.
            hits = re.findall(r'\(' + tag + r' "([^"]*)"\)', body)
            return hits[-1] if hits else None
        ref = grab("ref")
        if not ref:
            continue
        comps[ref] = {"value": grab("value"), "footprint": grab("footprint"),
                      "tstamp": grab_last("tstamps"), "pins": {}}
    for m in re.finditer(
            r'\(net\s+\(code "([^"]*)"\)\s*\(name "([^"]*)"\)(.*?)\n\t\t\)',
            text, re.S):
        name, body = m.group(2), m.group(3)
        for nm in re.finditer(
                r'\(node\s*\(ref "([^"]*)"\)\s*\(pin "([^"]*)"\)', body):
            ref, pin = nm.group(1), nm.group(2)
            if ref in comps:
                comps[ref]["pins"][pin] = name
    return nets, comps


NETS, COMPS = parse_netlist(NET_PATH)

# sanity: every netlist net has a code
assert len(NETS) >= 40, f"expected >=40 nets, got {len(NETS)}"
assert len(COMPS) == 80, \
    f"expected 80 components (64 electrical + J8-J13 + MH1-8 + U10 + C12V), got {len(COMPS)}"


# ------------------------------------------------------ footprint embedding

def fp_file(footprint_id):
    lib, name = footprint_id.split(":")
    return os.path.join(FP_ROOT, lib + ".pretty", name + ".kicad_mod")


def _balanced_replace(txt, opener_regex, replacement_fn):
    """Replace each balanced-paren block starting at a line matching
    opener_regex with replacement_fn(match_text). Returns new text."""
    result = []
    i = 0
    while True:
        m = re.search(opener_regex, txt[i:], re.M)
        if not m:
            result.append(txt[i:])
            break
        start = i + m.start()
        # scan forward counting parens from the opener's line start
        depth = 0
        j = start
        while j < len(txt):
            ch = txt[j]
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    j += 1
                    break
            j += 1
        block = txt[start:j]
        result.append(txt[i:start])
        result.append(replacement_fn(block))
        i = j
    return "".join(result)


def fp_embed(ref, x, y, rot=0):
    """Emit a board footprint instance of COMPS[ref] at (x, y) rot degrees.

    - embeds the library .kicad_mod body verbatim (real geometry, courtyard)
    - fresh uuid for every object (library bodies carry their own)
    - injects (net N "name") after each numbered pad's (layers ...) token
    - real Reference/Value, unhidden
    - (path ...) links the schematic symbol for parity checks
    """
    c = COMPS[ref]
    txt = open(fp_file(c["footprint"]), encoding="utf-8").read()
    txt = txt.replace("\r\n", "\n")
    lines = txt.split("\n")

    # strip library-only header: (footprint "Name" / version / generator* /
    # the body's own (layer "F.Cu") — we emit our own below
    body = []
    skipped_header = 0
    for ln in lines:
        s = ln.strip()
        if s.startswith('(footprint "'):
            skipped_header += 1
            continue
        if skipped_header and s.startswith(("(version", "(generator")):
            continue
        if skipped_header == 1 and s == '(layer "F.Cu")':
            skipped_header += 1
            continue
        body.append(ln)
    body_txt = "\n".join(body)

    # fresh uuids everywhere — NB: the replacement must be a lambda; a
    # plain f-string is evaluated ONCE, giving every graphic item in the
    # body the SAME uuid. pcbnew then de-duplicates on load with fresh
    # uuid4s, breaking byte-reproducibility of the gate-saved board.
    body_txt = re.sub(r'\(uuid "[0-9a-f-]*"\)',
                      lambda m: f'(uuid "{U()}")', body_txt)

    # Reference / Value properties -> real values, visible on silkscreen
    def repl_ref(block):
        return (f'(property "Reference" "{ref}" (at 0 -1 0) '
                f'(layer "F.SilkS")\n'
                f'\t\t(uuid "{U()}")\n'
                f'\t\t(effects (font (size 1 1) (thickness 0.15)) '
                f'(justify top))\n\t)')

    def repl_val(block):
        return (f'(property "Value" "{c["value"]}" (at 0 1 0) '
                f'(layer "F.Fab")\n'
                f'\t\t(uuid "{U()}")\n'
                f'\t\t(effects (font (size 1 1) (thickness 0.15)) '
                f'(justify top))\n\t)')

    body_txt = _balanced_replace(
        body_txt, r'^\t\(property "Reference" "REF\*\*"', repl_ref)
    body_txt = _balanced_replace(
        body_txt, r'^\t\(property "Value" "[^"]*"', repl_val)

    # nets into pads: insert (net ...) right after the pad's (layers ...) line
    def pad_net(block):
        m = re.search(r'\(pad "(\d+)"', block)
        padnum = m.group(1)
        net = c["pins"].get(padnum)
        if net is None or net.startswith("unconnected-"):
            return block
        lm = re.search(r'\(layers [^\n]*\)\n', block)
        if not lm:
            return block
        insert_at = lm.end()
        return (block[:insert_at] +
                f'\t\t(net {NETS[net]} "{net}")\n' +
                block[insert_at:])

    body_txt = _balanced_replace(body_txt, r'^\t\(pad "\d+"', pad_net)

    # KiCad-10 library graphics (fp_line/property/pad/...) often carry NO
    # uuid token; pcbnew then assigns a fresh uuid4 to each on save, which
    # breaks byte-reproducibility of the gate-saved board. Inject a
    # deterministic uuid into every item block that lacks one.
    def ensure_uuid(block):
        if "(uuid" in block:
            return block
        stripped = block.rstrip()
        i = stripped.rfind(")")
        ind = re.match(r"[ \t]*", block).group(0) + "\t"
        return stripped[:i] + f'{ind}(uuid "{U()}")\n' + stripped[i:]

    for _pat in (r'^\t*\(property "', r"^\t*\(fp_line\b", r"^\t*\(fp_rect\b",
                 r"^\t*\(fp_circle\b", r"^\t*\(fp_arc\b", r"^\t*\(fp_poly\b",
                 r"^\t*\(fp_text\b", r'^\t*\(pad "'):
        body_txt = _balanced_replace(body_txt, _pat, ensure_uuid)

    # empty-valued properties (Datasheet/Description) make KiCad regenerate
    # the field's uuid on each fresh parse — random uuid4s that break
    # byte-reproducibility of the gate-saved board. Stock KiCad libs omit
    # the blocks entirely and pcbnew re-adds them empty; deterministic text
    # instead: the footprint id doubles as a useful description.
    body_txt = body_txt.replace(
        '(property "Description" ""',
        f'(property "Description" "{c["footprint"]}"')
    body_txt = body_txt.replace(
        '(property "Datasheet" ""',
        '(property "Datasheet" "see schematic symbol"')
    for _name, _value in (("Datasheet", "see schematic symbol"),
                          ("Description", c["footprint"])):
        if f'(property "{_name}"' not in body_txt:
            block = (f'\t\t(property "{_name}" "{_value}" (at 0 0 0) '
                     f'(layer "F.Fab")\n'
                     f'\t\t\t(hide yes)\n'
                     f'\t\t\t(uuid "{U()}")\n'
                     f'\t\t\t(effects (font (size 1.27 1.27) (thickness 0.15)))\n'
                     f'\t\t)')
            m = re.search(r"(?m)^\t*\(attr ", body_txt)
            assert m, f"{ref}: no (attr anchor for {_name} property"
            body_txt = body_txt[:m.start()] + block + "\n" + body_txt[m.start():]

    # substitution must actually have happened — a silent no-match here is
    # what previously produced a board with only 1 loadable footprint
    assert "REF**" not in body_txt, f"{ref}: Reference substitution failed"
    assert f'"Reference" "{ref}"' in body_txt, f"{ref}: no Reference prop"
    assert f'"Value" "{c["value"]}"' in body_txt, f"{ref}: no Value prop"
    for padnum, net in c["pins"].items():
        if net.startswith("unconnected-"):
            continue  # no_connect pins: board pad stays netless
        assert f'(net {NETS[net]} "{net}")' in body_txt, \
            f"{ref} pad {padnum}: net injection failed"
    assert c["tstamp"] and c["tstamp"] != "/", f"{ref}: bad symbol tstamp"

    # emit instance — drop the library body's own final ")" (footprint closer)
    body_lines = [ln for ln in body_txt.split("\n") if ln.strip()]
    if body_lines and body_lines[-1].strip() == ")":
        body_lines.pop()
    L(1, f'(footprint "{c["footprint"]}"')
    L(2, '(layer "F.Cu")')
    L(2, f'(uuid "{U()}")')
    L(2, f'(at {fmt(x)} {fmt(y)} {rot})')
    L(2, f'(path "/{c["tstamp"]}")')
    L(2, '(sheetname "/")')
    L(2, '(sheetfile "aquarium_v0.kicad_sch")')
    for ln in body_lines:
        L(2, ln)
    L(1, ")")


# pad absolute positions (for routing endpoints)
# file coords: rotation CCW, Y down -> pad at (lx,ly) lands at
#   X = Px + lx*cos(t) + ly*sin(t);  Y = Py - lx*sin(t) + ly*cos(t)
PAD_CACHE = {}


def pad_pos(ref, padnum):
    """Absolute mm position of a pad center (uses the PLACEMENT table)."""
    key = (ref, padnum)
    if key in PAD_CACHE:
        return PAD_CACHE[key]
    x, y, rot = PLACEMENT[ref]
    c = COMPS[ref]
    txt = open(fp_file(c["footprint"]), encoding="utf-8").read()
    txt = txt.replace("\r\n", "\n")
    # pad block may be multi-line or single-line; grab the first (at ...)
    # token following the pad's opening
    m = re.search(
        r'\(pad "' + re.escape(padnum) + r'"[\s\S]{0,200}?\(at ([-\d.]+) '
        r'([-\d.]+)(?: [-\d.]+)?\)', txt)
    assert m, f"{ref}: pad {padnum} not found in {c['footprint']}"
    lx, ly = float(m.group(1)), float(m.group(2))
    t = math.radians(rot)
    px = x + lx * math.cos(t) + ly * math.sin(t)
    py = y - lx * math.sin(t) + ly * math.cos(t)
    PAD_CACHE[key] = (px, py)
    return px, py


def fp_bbox(ref):
    """Courtyard bbox (x1,y1,x2,y2) absolute, from the .pretty F.CrtYd."""
    x, y, rot = PLACEMENT[ref]
    c = COMPS[ref]
    txt = open(fp_file(c["footprint"]), encoding="utf-8").read()
    txt = txt.replace("\r\n", "\n")
    xs, ys = [], []
    def harvest(block):
        if '(layer "F.CrtYd")' not in block:
            return block
        for a, b in re.findall(r'\((?:xy|start|end|center|mid) '
                                r'([-\d.]+) ([-\d.]+)\)', block):
            xs.append(float(a))
            ys.append(float(b))
        if block.lstrip().startswith("(fp_circle"):
            m = re.search(r'\(center ([-\d.]+) ([-\d.]+)\)\s*\n?\s*'
                          r'\(end ([-\d.]+) ([-\d.]+)\)', block)
            cx, cy, ex, ey = map(float, m.groups())
            r = math.hypot(ex - cx, ey - cy)
            xs.extend((cx - r, cx + r))
            ys.extend((cy - r, cy + r))
        return block
    _balanced_replace(txt, r'\n\t\(fp_(?:line|rect|circle|poly|arc)\b',
                      harvest)
    assert xs, f"{ref}: no F.CrtYd geometry found in {c['footprint']}"
    t = math.radians(rot)
    corners = []
    for cx, cy in ((min(xs), min(ys)), (max(xs), min(ys)),
                   (min(xs), max(ys)), (max(xs), max(ys))):
        corners.append((x + cx * math.cos(t) + cy * math.sin(t),
                        y - cx * math.sin(t) + cy * math.cos(t)))
    xs2 = [p[0] for p in corners]
    ys2 = [p[1] for p in corners]
    return min(xs2), min(ys2), max(xs2), max(ys2)


# ------------------------------------------------------------- placements
# (ref: (x, y, rot)). Regions follow pcb_layout_notes.md and the MCPCB spans
# in extrusion_dims.md §3. Headers sit inside their MCPCB span (local x):
# J2 7-147, J3 149-289, J4 291-431, J5 433-573.
PLACEMENT = {}


def place(ref, x, y, rot=0):
    assert ref not in PLACEMENT, f"{ref} placed twice"
    PLACEMENT[ref] = (x, y, rot)


# One AL8860 channel cell, origin x0 (cell courtyards span x0+1.4 .. x0+28.45):
#   L  12x12 inductor at x0+8 rot 180: pin1 (SW side) RIGHT at x0+12.95,
#      pin2 (string cathode) LEFT at x0+3.05. 13.2 mm courtyard -> exclusive
#      x-window (nothing else shares x0+1.4..14.6).
#   D  SS3100 SMA at x0+16.5 y 4.5 rot 270: cathode pad UP at y 2.5 (24V bus),
#      anode pad DOWN at y 6.5 (short trace to SW pin).
#   U  TSOT-23-5 at x0+18.5 y 10 rot 0: SW pin1 top-left (x0+17.36, 9.05),
#      VIN pin5 top-right (x0+19.64, 9.05), SET pin4 bottom-right,
#      CTRL pin3 bottom-left, GND pin2 mid-left.
#   C100n 0603 at x0+22.2 y 9.05 rot 180: +24V pad (pin2) at x0+21.4
#      -> 1.76 mm from VIN pin.  GND pad (pin1) at x0+23.0.
#   C22 1210 at x0+26.05 y 9.05 rot 180: +24V pad (pin2) at x0+24.58
#      -> 4.91 mm from VIN pin.  GND pad at x0+27.75.
#   RSET 2512 at x0+21.5 y 16 rot 0: SET-side pad (pin1) at x0+19.6,
#      +24V pad (pin2) at x0+23.4. Kelvin path SET pin -> pin1 ~0.6 mm.
# SW->L pin1 trace ~4.5 mm (courtyard-limited: the 12 mm inductor cannot sit
# closer to the TSOT on a 20 mm-wide strip).
RSET_REF = {1: "R10", 2: "R11", 3: "R12", 4: "R13",
            5: "R14", 6: "R15", 7: "R16"}


def cell(uref, x0):
    ch = int(uref[1])
    place(f"L{ch}", x0 + 8.0, 10.0, 180)
    # D above the TSOT window: L's courtyard spans x x0+1.14..x0+14.86, so the
    # diode (courtyard 7.0 wide) must sit at x >= x0+15.1; y-band 2.75..6.25
    # is disjoint from U (8.3..11.7) and C20/C22 (8.32..10.65)
    place(f"D{ch}", x0 + 18.6, 4.5, 270)
    place(uref, x0 + 18.5, 10.0, 0)
    place(f"C{19 + ch}", x0 + 22.2, 9.05, 180)   # 100nF, pin2=+24V nearest
    place(f"C{9 + ch}", x0 + 26.05, 9.05, 180)   # 22uF, pin2=+24V nearest
    place(RSET_REF[ch], x0 + 21.5, 16.0, 0)
    return x0 + 1.4, x0 + 28.45


def build_placement():
    # ---- input + logic cluster, left end (x 0..100)
    place("J1", 8.0, 6.0, 0)          # DC 24V in terminal block
    place("F1", 12.0, 15.0, 0)         # fuse clips, inline along strip
    place("U10", 67.0, 5.0, 270)       # LM2596 buck module header (Rail B),
    #  north band (rot 270: pins run west, pin1 east at (67,5)); courtyard
    #  x 57.6-68.8 clears U8's (x<57.4) and J6's (x>76.2). p1 +24V (67,5),
    #  p2 GND (64.5,5), p3 +12V (61.9,5), p4 GND (59.4,5).
    place("C12V", 70.5, 10.0, 0)       # 10uF (1206) on +12V, pocket east of
    #  the +5V col x66 (moved 2026-09-15 twice: x71.5 sat in the /CTRL col
    #  wall, x66.9 pinned GND pad-1 against +5V); ties up via a B.Cu hop at
    #  x71.975 under the +3V3 horizontal
    place("J7", 32.0, 6.0, 0)          # rocker-switch loop terminal
    place("C2", 43.0, 13.0, 0)          # 220uF bulk (pad1 + at 43, pad2 at 48)
    place("C1", 52.0, 15.0, 90)         # 100nF input filter
    place("U8", 48.0, 5.0, 90)          # IRM-02-5 1x4 header, along strip
    place("U9", 58.5, 15.0, 0)          # AMS1117 SOT-223
    place("C3", 66.0, 15.5, 90)         # 1uF (5V side)
    place("C4", 70.0, 15.5, 90)         # 1uF (3V3 side)
    place("J6", 78.0, 5.0, 90)           # ESP32-C3 1x6 header, along strip
    for i in range(4):                  # R1-R4 1k series / R5-R8 100k pull-downs
        place(f"R{i+1}", 88.0 + 3.5 * i, 12.0, 90)
        place(f"R{i+5}", 88.0 + 3.5 * i, 17.5, 90)

    # ---- headers (pin 1 faces its driver cell) then channel cells
    place("J2", 109.0, 5.5, 270)        # MCPCB1 (span 7-147)
    cell("U1", 121.0)                   # white 1
    cell("U5", 155.0)                   # red
    cell("U6", 196.0)                   # blue (offset clears MH2)
    place("J3", 233.0, 5.5, 270)        # MCPCB2 (span 149-289)
    cell("U2", 245.0)                   # white 2
    cell("U3", 330.0)                   # white 3
    place("J4", 369.0, 5.5, 270)        # MCPCB3 (span 291-431)
    cell("U7", 398.0)                   # deep-red (offset clears MH3)
    cell("U4", 438.0)                   # white 4
    place("J5", 475.0, 5.5, 270)        # MCPCB4 (span 433-573)

    # ---- mounting holes (NPTH M3): 2 per board after the 4-board split.
    # Old positions kept (MH1-4); MH5-8 are the second hole per board, each
    # picked in a courtyard-clear, copper-clear band of its board (the
    # placement asserts below rejected the first-picked MH5/MH6/MH8 spots).
    place("MH1", 20.0, 4.0, 0)         # B1 west (y=4 clears J1/F1/J7)
    place("MH5", 112.0, 11.0, 0)       # B1 mid corridor: east of logic
    #  cluster, south of J2's courtyard (y7.27), north of J8's (y16.78)
    place("MH2", 190.0, 10.0, 0)       # B2 mid (clears U5/U6 cells)
    place("MH6", 290.0, 10.0, 0)       # B2 east end (no parts east of U2's
    #  cell; x=290 clears /CTRL_W's x=285.84 F.Cu descent to J10 p5 and the
    #  x=293.46/x=296 +24V escapes; J10's courtyard is south of y16.78)
    place("MH7", 308.0, 4.8, 0)        # B3 north band west of U3's cell
    #  (L3's 12x12 courtyard now spans x 331.1-344.9 - the old spot at
    #  x=330 overlapped it after the CYH127 inductor footprint fix)
    place("MH3", 390.0, 10.0, 0)       # B3 east end
    place("MH8", 495.0, 4.8, 0)        # B4 north band, 20 mm east of J5 pin1
    place("MH4", 560.0, 10.0, 0)       # B4 east end

    # ---- board joint headers (rot 270: pin1 = EAST end, pins run west)
    # South band y=18.55: pads clear the y=17.25 /R_K lane by 0.325 mm and
    # the RSET rows above; the 3.54 mm courtyard overhangs the south edge by
    # 0.32 mm (harmless — allowed in assert_rules). X positions sit in the
    # free courtyard windows between the RSET columns (see pcb_layout_notes
    # split record). 1x12 = seam 1, 1x10 = seams 2-3.
    place("J8", 129.71, 18.55, 270)    # B1 east joint, seam 1 -> J9
    place("J9", 210.50, 18.55, 270)    # B2 west joint, seam 1 -> J8
    place("J10", 296.00, 18.55, 270)   # B2 east joint, seam 2 -> J11
    place("J11", 327.00, 18.55, 270)   # B3 west joint, seam 2 -> J10
    place("J12", 395.80, 18.55, 270)   # B3 east joint, seam 3 -> J13
    place("J13", 448.50, 18.55, 270)   # B4 west joint, seam 3 -> J12


build_placement()

assert len(PLACEMENT) == len(COMPS), \
    f"placement covers {len(PLACEMENT)} of {len(COMPS)} components"

# --------------------------------------------------- placement self-asserts

JOINT_REFS = ("J8", "J9", "J10", "J11", "J12", "J13")


def board_of(ref):
    """Board number owning ref (by placement x anchor)."""
    x = PLACEMENT[ref][0]
    for n, x0, x1 in BOARDS:
        if x0 <= x <= x1:
            return n
    raise AssertionError(f"{ref} at x={x} outside every board window")


def assert_rules():
    errs = []
    # every part maps to a board and sits inside it. Exception: the joint
    # headers must sit hard against the south edge (their pads + 0.3 mm
    # copper clearance are all in-board) — the 3.54 mm courtyard box may
    # overhang the edge by up to 0.4 mm; that margin simply falls off the
    # board and is physically meaningless.
    for n, xw0, xw1 in BOARDS:
        for ref in PLACEMENT:
            if board_of(ref) != n:
                continue
            x1, y1, x2, y2 = fp_bbox(ref)
            ymax = BOARD_H + (0.4 if ref in JOINT_REFS else 0.0)
            if (x1 < xw0 or y1 < 0 or x2 > xw1 or y2 > ymax):
                errs.append(f"{ref}: outside board {n} window "
                            f"[{xw0},{xw1}] ({x1:.2f},{y1:.2f})-"
                            f"({x2:.2f},{y2:.2f})")
    # courtyard overlaps (except intentional same-cell stacking is NOT
    # allowed; every part must clear every other part's courtyard)
    refs = list(PLACEMENT)
    for i in range(len(refs)):
        for j in range(i + 1, len(refs)):
            a = fp_bbox(refs[i])
            b = fp_bbox(refs[j])
            if (a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]):
                errs.append(f"courtyard overlap: {refs[i]} vs {refs[j]}")
    # 100nF +24V pad within 2 mm of its driver VIN pin, 22uF within 5 mm
    # (high-side topology: netlist C20/C10 pin 2 = +24V, pin 1 = GND)
    for ch in range(1, 8):
        vin = pad_pos(f"U{ch}", "5")
        chf = pad_pos(f"C{19+ch}", "2")
        c22 = pad_pos(f"C{9+ch}", "2")
        d100 = math.hypot(vin[0] - chf[0], vin[1] - chf[1])
        d22 = math.hypot(vin[0] - c22[0], vin[1] - c22[1])
        if d100 > 2.0:
            errs.append(f"C{19+ch} +24V pad {d100:.2f} mm from U{ch} "
                        f"VIN (max 2)")
        if d22 > 5.0:
            errs.append(f"C{9+ch} +24V pad {d22:.2f} mm from U{ch} VIN "
                        f"(max 5)")
    # 3V3/logic section >= 10 mm courtyard gap from every AL8860 cell
    logic_refs = ["U8", "U9", "C3", "C4", "J6", "R1", "R2", "R3", "R4",
                  "R5", "R6", "R7", "R8"]
    for ch in range(1, 8):
        for ref in (f"U{ch}", f"L{ch}", f"D{ch}", f"C{19+ch}", f"C{9+ch}",
                    RSET_REF[ch]):
            b = fp_bbox(ref)
            for lref in logic_refs:
                a = fp_bbox(lref)
                if a[0] < b[2] + 10.0 and b[0] - 10.0 < a[2]:
                    errs.append(f"{lref} within 10 mm of {ref} (driver zone)")
    if errs:
        for e in errs:
            print("PLACEMENT VIOLATION:", e, file=sys.stderr)
        sys.exit(1)
    print(f"placement asserts OK: {len(PLACEMENT)} parts")


# ------------------------------------------------------------ board emitters

def emit_header():
    L(0, "(kicad_pcb")
    L(1, '(version 20260206)')
    L(1, '(generator "pcbnew")')
    L(1, '(generator_version "10.0")')
    L(1, "(general")
    L(2, "(thickness 1.6)")
    L(2, "(legacy_teardrops no)")
    L(1, ")")
    L(1, '(paper "A3")')
    L(1, "(layers")
    for spec in ('(0 "F.Cu" signal)', '(2 "B.Cu" signal)',
                 '(9 "F.Adhes" user "F.Adhesive")',
                 '(11 "B.Adhes" user "B.Adhesive")',
                 '(13 "F.Paste" user)', '(15 "B.Paste" user)',
                 '(5 "F.SilkS" user "F.Silkscreen")',
                 '(7 "B.SilkS" user "B.Silkscreen")',
                 '(1 "F.Mask" user)', '(3 "B.Mask" user)',
                 '(17 "Dwgs.User" user "User.Drawings")',
                 '(19 "Cmts.User" user "User.Comments")',
                 '(21 "Eco1.User" user "User.Eco1")',
                 '(23 "Eco2.User" user "User.Eco2")',
                 '(25 "Edge.Cuts" user)', '(27 "Margin" user)',
                 '(31 "F.CrtYd" user "F.Courtyard")',
                 '(29 "B.CrtYd" user "B.Courtyard")',
                 '(35 "F.Fab" user)', '(33 "B.Fab" user)'):
        L(2, spec)
    L(1, ")")
    L(1, "(setup")
    L(2, "(pad_to_mask_clearance 0)")
    L(2, "(tenting (front no) (back no))")
    L(2, "(pcbplotparams")
    L(3, "(layerselection 0x00010fc_ffffffff)")
    L(3, "(plot_on_all_layers_selection 0x0000000_00000000)")
    L(3, "(disableapertmacros no)")
    L(3, "(usegerberextensions no)")
    L(3, "(usegerberattributes yes)")
    L(3, "(usegerberadvancedattributes yes)")
    L(3, "(creategerberjobfile yes)")
    L(3, "(dashed_line_dash_ratio 12.000000)")
    L(3, "(dashed_line_gap_ratio 3.000000)")
    L(3, "(svgprecision 4)")
    L(3, "(plotframeref no)")
    L(3, "(viasonmask no)")
    L(3, "(mode 1)")
    L(3, "(useauxorigin no)")
    L(3, "(hpglpennumber 1)")
    L(3, "(hpglpenspeed 20)")
    L(3, "(hpglpendiameter 15.000000)")
    L(3, "(pdf_front_meta_property 0)")
    L(3, "(pdf_back_meta_property 1)")
    L(3, "(dxfpolygonmode yes)")
    L(3, "(dxfimperialunits yes)")
    L(3, "(dxfusepcbnewfont yes)")
    L(3, "(psnegative no)")
    L(3, "(psa4offset1 no)")
    L(3, "(psreference no)")
    L(3, "(pstype 3)")
    L(3, "(psoutputpro false)")
    L(3, "(plotreference yes)")
    L(3, "(plotvalue yes)")
    L(3, "(plotfptext yes)")
    L(3, "(plotinvisibletext no)")
    L(3, "(sketchpadsonfab no)")
    L(3, "(subtractmaskfromsilk no)")
    L(3, "(plotmode 1)")
    L(3, "(coordmode 2)")
    L(3, "(outputformat 1)")
    L(3, "(mirror no)")
    L(3, "(drillshape 0)")
    L(3, "(scaleselection 1)")
    L(3, "(outputdirectory \"gerbers/\")")
    L(2, ")")
    L(1, ")")
    # net table: net 0 + every netlist net, codes verbatim from the netlist
    L(1, '(net 0 "")')
    for name, code in sorted(NETS.items(), key=lambda kv: kv[1]):
        L(1, f'(net {code} "{name}")')


def emit_edge(x0, x1):
    pts = [(x0, 0), (x1, 0), (x1, BOARD_H), (x0, BOARD_H), (x0, 0)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        L(1, f'(gr_line (start {fmt(ax)} {fmt(ay)}) (end {fmt(bx)} {fmt(by)}) '
             f'(stroke (width 0.05) (type solid)) (layer "Edge.Cuts") '
             f'(uuid "{U()}"))')


def emit_footprints(n):
    for ref in sorted(PLACEMENT, key=lambda r: PLACEMENT[r][0]):
        if board_of(ref) != n:
            continue
        x, y, rot = PLACEMENT[ref]
        fp_embed(ref, x, y, rot)


def emit_routes_extra(x0, x1):
    """Overlay hook for the routing agents: segments + vias from
    ROUTES_EXTRA.json next to this script, merged verbatim into the board.
    Format:
      {"routes": [{"net": "...", "layer": "F.Cu", "width": 0.5,
                   "pts": [[x, y], [x, y], ...]}, ...],       # polylines
       "vias":   [{"net": "...", "x": ..., "y": ...}, ...]}  # 0.5/0.3 JLC min
    The file is a first-class source of truth (checked in), so the board
    regenerates deterministically from gen_pcb.py + ROUTES_EXTRA.json.

    WINDOW FILTER (4-board split): a segment is emitted only when BOTH
    endpoints lie inside the board's x-window, a via only when its centre
    does. Anything crossing a seam is dropped automatically — those nets
    now travel through the joint headers (J8-J13). Cell-local routes (SW
    loops, per-cell feeds, J2-J5 escapes, W lanes, K descents, logic
    cluster) are fully inside one window and survive unchanged."""
    p = os.path.join(HERE, "ROUTES_EXTRA.json")
    if not os.path.exists(p):
        return
    with open(p, encoding="utf-8") as f:
        data = json.load(f)

    def inside(x):
        return x0 - 1e-6 <= x <= x1 + 1e-6

    for r in data.get("routes", []):
        code = NETS[r["net"]]
        pts = [(float(a), float(b)) for a, b in r["pts"]]
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            if not (inside(ax) and inside(bx)):
                continue
            # NB: track/via net tokens take the CODE ONLY — KiCad 10's parser
            # rejects a name string here ("Expecting ')'"); pads are the only
            # items that may carry (net N "name").
            L(1, f'(segment (start {fmt(ax)} {fmt(ay)}) '
                 f'(end {fmt(bx)} {fmt(by)}) '
                 f'(width {fmt(r["width"])}) (layer "{r["layer"]}") '
                 f'(net {code}) (uuid "{U()}"))')
    for v in data.get("vias", []):
        if not inside(float(v["x"])):
            continue
        code = NETS[v["net"]]
        L(1, f'(via (at {fmt(v["x"])} {fmt(v["y"])}) (size 0.5) (drill 0.3) '
                 f'(layers "F.Cu" "B.Cu") '
                 f'(net {code}) (uuid "{U()}"))')


# driver cells (ref, x0) — same origins as build_placement()
CELLS = [("U1", 121.0), ("U5", 155.0), ("U6", 196.0), ("U2", 245.0),
         ("U3", 330.0), ("U7", 398.0), ("U4", 438.0)]


def gnd_smd_pads():
    """(ref, pad) for every SMD pad on GND. Thru-hole GND pads (J1/J6/U8/
    C2/F1) bond to the B.Cu pour directly and need no via."""
    hits = []
    for ref in sorted(COMPS):
        c = COMPS[ref]
        txt = open(fp_file(c["footprint"]), encoding="utf-8").read()
        for padnum, net in sorted(c["pins"].items()):
            if net != "GND":
                continue
            m = re.search(r'\(pad "' + re.escape(padnum) + r'" (\w+)', txt)
            if m and m.group(1) == "smd":
                hits.append((ref, padnum))
    return hits


def emit_zones(n, x0, x1):
    """GND: whole-board B.Cu pour + one F.Cu thermal island per driver cell,
    stitched to the pour by 10 vias per island, plus a via in every SMD GND
    pad. R8 pin1's pad sits over /B_J23's B.Cu lane (y18.15, x96.3+) so its
    via drops south of the pad row instead of pad-center. No fills are
    written here — the gate is `kicad-cli pcb drc --refill-zones
    --save-board`, which computes and persists them.

    Per-board after the split: the pour rect follows the board window, the
    islands/vias/pad-vias only cover this board's cells and parts, and the
    R5-R8 GND bridge network (x72-100) is B1-only."""
    assert "GND" in NETS, "no GND net in netlist"
    gnd = NETS["GND"]

    def via(x, y):
        L(1, f'(via (at {fmt(x)} {fmt(y)}) (size 0.5) (drill 0.3) '
             f'(layers "F.Cu" "B.Cu") (net {gnd}) (uuid "{U()}"))')

    def seg(x1, y1, x2, y2):
        L(1, f'(segment (start {fmt(x1)} {fmt(y1)}) (end {fmt(x2)} {fmt(y2)}) '
             f'(width 0.3) (layer "F.Cu") (net {gnd}) (uuid "{U()}"))')

    def zone(layer, priority, pts):
        L(1, "(zone")
        L(2, f'(net {gnd}) (net_name "GND")')
        L(2, f'(uuid "{U()}")')
        L(2, f'(layer "{layer}")')
        L(2, "(hatch edge 0.5)")
        L(2, f"(priority {priority})")
        L(2, "(connect_pads (clearance 0.2))")
        # 0.2 (not 0.25) so the 0.24-wide channels between adjacent J9/J10
        # PTH pad carve circles stay open: they are the only path between
        # the J9 GND pocket (south body + y15.9-16.5 strip, holding the p3/p4
        # ties) and the west pour body that wraps /R_K's west end.
        L(2, "(min_thickness 0.2)")
        L(2, "(filled_areas_thickness no)")
        # thermal_gap 0.25 (not 0.5): a 0.5 gap puts r1.35 relief rings
        # around the joint-header GND PTH pads, which then sit 0.134 from the
        # neighbouring pad carves (2.54 pitch) and seal the J9 GND pocket
        # off from the south body. r1.1 rings leave a 0.384 channel.
        L(2, "(fill yes (thermal_gap 0.25) (thermal_bridge_width 0.5))")
        L(2, "(polygon")
        L(3, "(pts")
        for x, y in pts:
            L(4, f"(xy {fmt(x)} {fmt(y)})")
        L(3, ")")
        L(2, ")")
        L(1, ")")

    # bottom pour to the board's south edge: the y17.7-19.5 body bonds the
    # joint-header GND PTH pads (J8-J13 p3/p4) directly and wraps west
    # around /R_K's west end (the pour runs unbroken at x158.6-159.1,
    # between the /CTRL_W and /CTRL_DR vertical carves). The J9 GND pocket
    # reaches it through the 0.24-wide pad-row channels (hence
    # min_thickness 0.2 above). Item-less fragments are island-removed.
    zone("B.Cu", 1, [(x0 + 0.5, 0.5), (x1 - 0.5, 0.5),
                     (x1 - 0.5, 19.5), (x0 + 0.5, 19.5)])
    # per-cell F.Cu islands + stitching vias. Constraints learned from DRC:
    #  - SW/+24V/K nets are 0.3-class; the CTRL drop B.Cu vertical x0+16.1
    #    spans y1.0-10.35, so the whole west strip is blocked below y11.5.
    #  - /R_A's B.Cu lane (patch5: y12.7) passes under cells U1/U5.
    #  - /B_K and /DR_K B.Cu descents at x0+23 run through cells U6/U4.
    #  - hole-to-hole >= 0.6 between all vias.
    # West band is therefore just 2 vias at y12; east band 4 (3 for U6/U4,
    # shifted west of the descents). C100n pin1 via-in-pad is skipped for
    # U6/U4 (a via there lands on the descent); the island fill bonds it.
    for uref, xc0 in CELLS:
        if not (x0 <= xc0 + 21.0 <= x1):    # island centre inside window
            continue
        # east edge 28.4 reaches past the C22u pin1 GND pads (26.325-27.725)
        # so the island fill bonds them; the pin2 +24V pads (29.325+) stay
        # 0.925 clear. The +24V y11 riser splits the extension, but the
        # C22u pad is in the north half, which joins the main island fill
        # through the west neck (west of the riser cap at 24.825).
        zone("F.Cu", 2, [(xc0 + 15.5, 7.6), (xc0 + 28.4, 7.6),
                         (xc0 + 28.4, 12.4), (xc0 + 15.5, 12.4)])
        spots = [(16.0, 12.0), (16.65, 12.0)]
        if uref in ("U6", "U4"):
            spots += [(21.9, 8.0), (21.9, 10.1), (21.9, 12.0)]
        else:
            spots += [(22.1, 8.0), (22.9, 8.0), (22.2, 12.0), (22.9, 12.0)]
        for dx, dy in spots:
            via(xc0 + dx, dy)
    # U6/U4 C100n pin1 vias would land on the K descents, U3/U4 C22u pin1
    # vias land in B.Cu pockets sealed by the J4/J5 pad rows (0.24 gaps
    # < min_thickness) — the pads bond to the extended island fill instead.
    skip_via_in_pad = {("R5", "1"), ("R6", "1"), ("R7", "1"), ("R8", "1"),
                       ("C25", "1"), ("C23", "1"),
                       ("C12", "1"), ("C13", "1")}
    for ref, padnum in gnd_smd_pads():
        if (ref, padnum) in skip_via_in_pad:
            continue
        if board_of(ref) != n:
            continue
        px, py = pad_pos(ref, padnum)
        via(px, py)
    if n == 1:
        # R5-R8 pin1 (GND) pads at y18.325 sit south of the pour (over the
        # chain lanes), so they bridge on F.Cu instead. The CTRL via_B
        # returns fence the B.Cu pour into a west fragment (x<73.5) and an
        # east fragment, so this one F.Cu network also stitches the two
        # pour halves together (B1-only geometry):
        #   via (72.4,16.2) -> west pour
        #   tie y18.0 over R5-R7 pin1 pads, riser east at y19.5 (under DR's
        #   return via, 0.25 clear), down x99.9 to via (99.9,14.5) -> east
        #   pour.
        seg(72.4, 18.0, 95.4, 18.0)        # ties R5+R6+R7 pin1 pads
        seg(72.4, 16.2, 72.4, 19.5)        # west riser + south drop
        via(72.4, 16.2)
        seg(72.4, 19.5, 99.9, 19.5)        # pours-under the CTRL return fence
        seg(99.9, 14.5, 99.9, 19.5)        # east riser, via at the south end
        seg(98.9, 18.325, 99.9, 18.325)    # R8 pin1 east edge -> riser
        via(99.9, 14.5)


def emit_silk_texts(n, x0, x1):
    """Board-level silkscreen: per-board title, polarity marks, pin-1 dots."""
    def gr_text(txt, x, y, rot=0, size=1.0):
        just = " top" if rot in (0,) else ""
        L(1, f'(gr_text "{txt}"')
        L(2, f'(at {fmt(x)} {fmt(y)} {rot})')
        L(2, '(layer "F.SilkS")')
        L(2, f'(uuid "{U()}")')
        L(2, f'(effects (font (size {fmt(size)} {fmt(size)}) '
             f'(thickness 0.15)))')
        L(1, ")")

    def pin1_dot(x, y):
        L(1, f'(gr_circle (center {fmt(x)} {fmt(y)}) '
             f'(end {fmt(x + 0.4)} {fmt(y)}) '
             f'(stroke (width 0.15) (type solid)) (fill no) '
             f'(layer "F.SilkS") (uuid "{U()}"))')

    gr_text(f"AQUARIUM V0 DRIVER  BOARD {n}  24V", x0 + 6.0, 2.0, 0, 1.0)
    if n == 1:
        gr_text("24V IN -> FUSE -> SWITCH", 10.0, 11.2, 0, 0.8)
        gr_text("ESP32", 80.0, 10.5, 90, 0.8)
        gr_text("IRM-02-5", 47.5, 10.2, 90, 0.8)
    # MCPCB header pin1 marks + polarity: pin1 (+, W_A), pin2 (-, W_K)
    for href in ("J2", "J3", "J4", "J5"):
        if board_of(href) != n:
            continue
        p1 = pad_pos(href, "1")
        pin1_dot(p1[0] - 1.6, p1[1])
        gr_text("+", p1[0] - 1.6, p1[1] + 2.2, 0, 1.0)
        p2 = pad_pos(href, "2")
        gr_text("-", p2[0] - 1.6, p2[1] + 2.2, 0, 1.0)
    # joint headers: pin 1 is the EAST end (rot 270) — dot sits east of it
    for jref in JOINT_REFS:
        if board_of(jref) != n:
            continue
        p1 = pad_pos(jref, "1")
        pin1_dot(p1[0] + 1.6, p1[1])
    # channel labels above each cell (driver end)
    labels = {"U1": "W1", "U2": "W2", "U3": "W3", "U4": "W4",
              "U5": "RED", "U6": "BLUE", "U7": "DEEP-RED"}
    for (uref, xc0) in CELLS:
        if not (x0 <= xc0 + 18.5 <= x1):
            continue
        gr_text(labels[uref], xc0 + 20.5, 19.3, 0, 0.8)


# ------------------------------------------------------------------- main

def main():
    # --board N: write only that board's files. All 4 boards are still
    # EMITTED in a fixed order first — the uuid counter U() runs across the
    # whole sequence, so per-board uuids are identical whether or not
    # other boards' files get written (keeps --board runs reproducible
    # against full runs).
    wanted = None
    if "--board" in sys.argv:
        wanted = {int(sys.argv[sys.argv.index("--board") + 1])}
        assert wanted <= {n for n, _, _ in BOARDS}, "board must be 1..4"
    assert_rules()
    with open(PRO_TEMPLATE, encoding="utf-8") as f:
        pro_base = json.load(f)

    for n, x0, x1 in BOARDS:
        del out[:]
        emit_header()
        emit_edge(x0, x1)
        emit_footprints(n)
        emit_routes_extra(x0, x1)
        emit_silk_texts(n, x0, x1)
        emit_zones(n, x0, x1)
        L(0, ")")
        if wanted is not None and n not in wanted:
            continue
        pcb_path = os.path.join(HERE, f"aquarium_v0_board{n}.kicad_pcb")
        with open(pcb_path, "w", encoding="utf-8") as f:
            f.write("\n".join(out) + "\n")
        print(f"wrote {pcb_path} ({len(out)} lines)")

        # board design rules + netclass assignments into a per-board .pro
        # (fresh copy of the schematic template each time)
        pro = json.loads(json.dumps(pro_base))
        pro["net_settings"]["classes"].append({
            "name": "Power_12V", "bus_width": 12, "clearance": 0.3,
            "diff_pair_gap": 0.25, "diff_pair_via_gap": 0.25,
            "diff_pair_width": 0.2, "track_width": 0.5,
            "via_diameter": 0.8, "via_drill": 0.4, "wire_width": 6})
        pro["board"] = {
        "design_settings": {
            "defaults": {},
            "drc_exclusions": [],
            "rules": {
                "min_clearance": 0.15,
                "min_track_width": 0.15,
                "min_via_diameter": 0.5,
                "min_via_annular_width": 0.1,
                "min_through_hole_diameter": 0.3,
                "min_hole_to_hole": 0.3,
                "min_hole_clearance": 0.15,
                "min_copper_edge_clearance": 0.3,
                "min_silk_clearance": 0.0,
                "min_text_height": 0.8,
                "min_text_thickness": 0.12,
            },
            "rule_severities": {
                "unconnected_items": "error",
                # our embedded footprint bodies are intentionally modified
                # copies of the library ones (real refdes, fresh uuids)
                "lib_footprint_mismatch": "ignore",
                # KiCad 10.0.6 renamed the check; boards embed modified
                # copies of lib footprints by design
                "lib_footprint_issues": "ignore",
                # dense 20 mm strip: refdes/labels over pads and each other
                # are unavoidable; fab mask openings clip silk anyway
                "silk_over_copper": "ignore",
                "silk_overlap": "ignore",
                "silk_edge_clearance": "ignore",
            },
            "track_widths": [0.25, 0.5, 0.8, 1.0],
            "via_dimensions": [{"diameter": 0.5, "drill": 0.3}],
        },
        "file_descriptor": {"layer": "F.Cu"},
        }
        assign = {}
        for name in NETS:
            if name in ("+24V",) or re.match(r"Net-\(U\d-SW\)", name):
                assign[name] = "Power_24V"
            elif name == "+12V":
                assign[name] = "Power_12V"
            elif name.endswith("_A") and name != "SW_A":
                assign[name] = "LED_Anode"
            elif name.endswith("_K"):
                assign[name] = "LED_Cathode"
        pro["net_settings"]["netclass_assignments"] = assign
        pro_path = os.path.join(HERE, f"aquarium_v0_board{n}.kicad_pro")
        with open(pro_path, "w", encoding="utf-8") as f:
            json.dump(pro, f, indent=2)
        print(f"updated {pro_path}")


if __name__ == "__main__":
    main()