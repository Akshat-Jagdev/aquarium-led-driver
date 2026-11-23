#!/usr/bin/env python3
"""Generate printable component-placement (assembly) diagrams for aquarium_v0
boards 1-4. Embeds true-geometry kicad-cli SVG artwork (svg/boardN.svg) and
overlays readable refdes/value labels, pin-1 dots, polarity marks, and a
stuffing BOM per board. Output: assembly_diagram.html (A4 landscape pages).

Usage: python3 gen_assembly.py
"""
import re, math, json, html
from pathlib import Path

HERE = Path(__file__).parent
KICAD = HERE.parent / "kicad_project"
SVGDIR = HERE / "svg"

BOARDS = [
    (1, "Input & ESP32 controller  (24V IN → FUSE → SWITCH)"),
    (2, "RED + BLUE channels"),
    (3, "W3 channel"),
    (4, "DEEP-RED + W4 channels"),
]

# ---------------- sexpr-lite parser ----------------
def tokenize(s):
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c in " \t\r\n": i += 1; continue
        if c == "(" or c == ")": yield c; i += 1; continue
        if c == '"':
            j = i + 1
            while j < n:
                if s[j] == "\\": j += 2; continue
                if s[j] == '"': break
                j += 1
            yield s[i+1:j]; i = j + 1; continue
        j = i
        while j < n and s[j] not in " \t\r\n()\"": j += 1
        yield s[i:j]; i = j

def parse(s):
    stack, cur = [], []
    for t in tokenize(s):
        if t == "(":
            new = []
            cur.append(new); stack.append(cur); cur = new
        elif t == ")":
            child = cur
            if stack:
                cur = stack.pop()
            else:
                return child
        else:
            cur.append(t)
    return cur[0] if cur and len(cur) == 1 else cur

def sym(node):  # s-expression node -> (tag, args, subnodes)
    return node[0], node[1:], [x for x in node[1:] if isinstance(x, list)]

def find_all(node, tag):
    out = []
    for x in node[1:] if isinstance(node, list) else []:
        if isinstance(x, list) and x and x[0] == tag: out.append(x)
    return out

def find1(node, tag):
    r = find_all(node, tag)
    return r[0] if r else None

# ---------------- data extraction ----------------
def get_props(fp):
    d = {}
    for p in find_all(fp, "property"):
        if len(p) >= 3 and isinstance(p[2], str):
            d[p[1]] = p[2]
    return d

def parse_pads(fp):
    pads = []
    for pd in find_all(fp, "pad"):
        num = pd[1]; shape = pd[2]
        at = find1(pd, "at"); size = find1(pd, "size"); drill = find1(pd, "drill")
        net = find1(pd, "net")
        if not (at and size): continue
        pr = float(at[3]) if len(at) > 3 else 0.0
        pads.append(dict(
            num=num, shape=shape,
            x=float(at[1]), y=float(at[2]), prot=pr,
            w=float(size[1]), h=float(size[2]) if len(size) > 2 else float(size[1]),
            drill=float(drill[1]) if drill else 0.0,
            net=net[2] if net and len(net) > 2 else "",
        ))
    return pads

def edge_bbox(pcb):
    xs, ys = [], []
    for it in pcb[1:]:
        if not (isinstance(it, list) and it and it[0] in
                ("gr_line", "gr_rect", "gr_circle", "gr_arc", "gr_poly", "gr_bbox")): continue
        if not any(isinstance(x, list) and x and x[0] == "layer"
                   and x[1] in ("Edge.Cuts", "Edge_Cuts") for x in it[1:]):
            continue
        for sub in it[1:]:
            if not (isinstance(sub, list) and sub): continue
            if sub[0] in ("start", "end", "mid") and len(sub) >= 3:
                xs.append(float(sub[1])); ys.append(float(sub[2]))
        c = find1(it, "center"); e = find1(it, "end")
        if it[0] == "gr_circle" and c and e and len(c) >= 3 and len(e) >= 3:
            r = math.hypot(float(e[1]) - float(c[1]), float(e[2]) - float(c[2]))
            xs += [float(c[1]) - r, float(c[1]) + r]; ys += [float(c[2]) - r, float(c[2]) + r]
        if it[0] == "gr_rect":
            s2 = find1(it, "start"); e2 = find1(it, "end")
            if s2 and e2:
                xs += [float(s2[1]), float(e2[1])]; ys += [float(s2[2]), float(e2[2])]
    return (min(xs), min(ys), max(xs), max(ys)) if xs else (0, 0, 100, 20)

def rot_pt(x, y, deg, conv):
    t = math.radians(deg)
    if conv == 0:   # candidate A: x'=x·c−y·s, y'=x·s+y·c
        return x*math.cos(t) - y*math.sin(t), x*math.sin(t) + y*math.cos(t)
    else:           # candidate B: x'=x·c+y·s, y'=−x·s+y·c
        return x*math.cos(t) + y*math.sin(t), -x*math.sin(t) + y*math.cos(t)

def load_board(n):
    txt = (KICAD / f"aquarium_v0_board{n}.kicad_pcb").read_text()
    pcb = parse(txt)
    fps = []
    for fp in [x for x in pcb[1:] if isinstance(x, list) and x and x[0] == "footprint"]:
        props = get_props(fp)
        at = find1(fp, "at")
        layer = find1(fp, "layer")
        attr = find1(fp, "attr")
        fps.append(dict(
            ref=props.get("Reference", "?"), value=props.get("Value", "?"),
            pkg=fp[1].split(":")[-1],
            x=float(at[1]), y=float(at[2]),
            rot=float(at[3]) if len(at) > 3 else 0.0,
            layer=layer[1] if layer else "F.Cu",
            tht=bool(attr and any(a.startswith("through_hole") for a in attr[1:])),
            ref_off=(0.0, 0.0),
            pads=parse_pads(fp),
            _fp=fp,
        ))
        # ref silk offset (first property "Reference" at dx dy)
        for p in find_all(fp, "property"):
            if len(p) > 1 and p[1] == "Reference":
                pa = find1(p, "at")
                if pa and len(pa) >= 3:
                    fps[-1]["ref_off"] = (float(pa[1]), float(pa[2]))
    return pcb, fps, edge_bbox(pcb)

def svg_texts(path):
    """refdes -> absolute silk text position, from kicad-cli SVG (mm, y-down)."""
    s = path.read_text()
    out = {}
    for m in re.finditer(
        r'<text x="(-?[\d.]+)" y="(-?[\d.]+)"([^>]*)>(.*?)</text>', s, re.S):
        x, y, attrs, body = float(m.group(1)), float(m.group(2)), m.group(3), m.group(4)
        t = re.sub(r"<[^>]+>", "", body).strip()
        t = html.unescape(t)
        if re.fullmatch(r"[A-Z]{1,2}\d+[A-Z]?", t):
            out.setdefault(t, (x, y))
    return out

def pick_rotation_conv(fps, silks, bb):
    """Validate rotation convention against silk refdes anchor positions.
    silks are in SVG (board-local) coords; footprints in absolute file coords."""
    best, besterr = 0, 1e18
    mnx, mny = bb[0], bb[1]
    for conv in (0, 1):
        err = 0.0; cnt = 0
        for f in fps:
            if f["ref"] not in silks or not f["ref_off"]: continue
            dx, dy = rot_pt(*f["ref_off"], f["rot"], conv)
            px, py = f["x"] + dx - mnx, f["y"] + dy - mny
            sx, sy = silks[f["ref"]]
            err += math.hypot(px - sx, py - sy); cnt += 1
        if cnt and err < besterr: best, besterr = conv, err
    return best, (besterr / max(1, cnt))

# ---------------- classification / colors ----------------
def classify(f):
    r = f["ref"]; v = f["value"]; p = f["pkg"]
    is_led = "LED" in p or "5050" in p or "2835" in p or "LED" in v.upper()
    if r.startswith("MH"): return "mh", "#999999"
    if r.startswith("U"):  return "u", "#d92b2b"
    if r.startswith("D"):  return ("led", "#c9a300") if is_led else ("d", "#e07800")
    if r.startswith("R"):  return "r", "#44586e"
    if r.startswith("C"):  return "c", "#1f61c4"
    if r.startswith("L"):  return "l", "#148a4c"
    if r.startswith("J"):  return "j", "#8a5a2b"
    if r.startswith("F"):  return "f", "#b23db2"
    return "x", "#555555"

CLS_NAME = {"u": "IC / module", "d": "Diode (polarity!)", "led": "LED (polarity!)",
            "r": "Resistor", "c": "Capacitor", "l": "Inductor",
            "j": "Connector / header", "f": "Fuse", "mh": "Mounting hole", "x": "Other"}

# ---------------- overlay SVG ----------------
def overlay(fps, conv, bb, W, H):
    mnx, mny = bb[0], bb[1]
    o = []
    placed = []  # label bboxes (board-local mm) for collision avoidance

    def esc(s): return html.escape(s)

    def text_w(s, fs): return len(s) * fs * 0.62

    band = {"top": [], "bot": []}  # parked callout labels per band: (x0, x1, row)

    def place(cx, y, s, fs, dy_offs):
        """try y offsets (mm) until no overlap with placed labels.
        returns (y, ok)"""
        w2 = text_w(s, fs) / 2
        for dy in dy_offs:
            yy = y + dy
            r = (cx - w2, yy - fs, cx + w2, yy + 0.3)
            if not any(r[0] < p[2] + 0.3 and p[0] < r[2] + 0.3 and
                       r[1] < p[3] + 0.2 and p[1] < r[3] + 0.2 for p in placed):
                placed.append(r)
                return yy, True
        return y, False

    def band_slot(cx, s, fs, which):
        """find (x, row) in the top/bottom callout band with no overlap; wraps rows"""
        w2 = text_w(s, fs) / 2 + 0.7
        row = 0
        while True:
            inrow = [p for p in band[which] if p[2] == row]
            x = cx
            for _ in range(80):
                hit = next((p for p in inrow if x - w2 < p[1] and p[0] < x + w2), None)
                if hit is None: break
                x = hit[1] + w2
            if x + w2 <= W + 1.0 or not inrow:
                band[which].append((x - w2, x + w2, row))
                return x, row
            row += 1

    for f in sorted(fps, key=lambda f: f["x"]):
        if f["ref"].startswith("MH"): continue
        cls, color = classify(f)
        # pad bbox in board coords
        pts = []
        for p in f["pads"]:
            # pad centre (ignore tiny pad rot for bbox)
            px, py = rot_pt(p["x"], p["y"], f["rot"], conv)
            pts.append((f["x"] + px, f["y"] + py, p))
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        pw = max((p[2]["w"] for p in pts), default=1.0)
        ph = max((p[2]["h"] for p in pts), default=1.0)
        x0, x1 = min(xs) - pw/2 - 0.6, max(xs) + pw/2 + 0.6
        y0, y1 = min(ys) - ph/2 - 0.6, max(ys) + ph/2 + 0.6
        sx, sy = x0 - mnx, y0 - mny
        w, h = x1 - x0, y1 - y0
        dash = ' stroke-dasharray="1,0.5"' if cls == "led" else ""
        o.append(f'<rect x="{sx:.2f}" y="{sy:.2f}" width="{w:.2f}" height="{h:.2f}" rx="0.6" '
                 f'fill="{color}" fill-opacity="0.14" stroke="{color}" stroke-width="0.35"{dash}/>')
        # pin-1 dot (multi-pad parts with pad "1")
        padnums = [p["num"] for p in f["pads"]]
        p1 = next((p for p in pts if p[2]["num"] == "1"), None)
        if p1 and (len(f["pads"]) > 2):
            o.append(f'<circle cx="{p1[0]-mnx:.2f}" cy="{p1[1]-mny:.2f}" r="0.55" fill="{color}"/>')
        # diode cathode mark (pads named A / K)
        cath = next((p for p in pts if p[2]["num"].upper() in ("K", "CATHODE")), None)
        anode = next((p for p in pts if p[2]["num"].upper() in ("A", "ANODE")), None)
        if cath and anode:
            cx, cy = cath[0] - mnx, cath[1] - mny
            if abs(cath[0] - anode[0]) >= abs(cath[1] - anode[1]):
                dx = 1.0 if cath[0] > anode[0] else -1.0; dy = 0.0
            else:
                dx = 0.0; dy = 1.0 if cath[1] > anode[1] else -1.0
            ex, ey = cx - dx * (w/2 - 0.3) * (1 if dx else 0), cy - dy * (h/2 - 0.3) * (1 if dy else 0)
            o.append(f'<line x1="{cx:.2f}" y1="{cy:.2f}" x2="{ex:.2f}" y2="{ey:.2f}" '
                     f'stroke="{color}" stroke-width="0.7"/>')
            o.append(f'<text x="{cx + dx*1.1:.2f}" y="{cy + dy*1.1 + 0.5:.2f}" font-size="1.6" '
                     f'font-weight="700" fill="{color}" text-anchor="middle">K</text>')
        # labels (collision-avoided, with callout-band fallback + leader lines)
        lx = (x0 + x1)/2 - mnx
        ry, ok = place(lx, y0 - mny - 0.7, f["ref"], 2.6, (0, -2.9, +2.9))
        if ok:
            o.append(f'<text x="{lx:.2f}" y="{ry:.2f}" font-size="2.6" font-weight="700" '
                     f'fill="{color}" text-anchor="middle" font-family="Helvetica,Arial">{esc(f["ref"])}</text>')
        else:
            bx, row = band_slot(lx, f["ref"], 2.6, "top")
            by = -2.4 - row * 3.9
            placed.append((bx - text_w(f["ref"], 2.6)/2, by - 2.6, bx + text_w(f["ref"], 2.6)/2, by + 0.3))
            o.append(f'<line x1="{lx:.2f}" y1="{sy:.2f}" x2="{bx:.2f}" y2="{by + 0.3:.2f}" '
                     f'stroke="{color}" stroke-width="0.15"/>')
            o.append(f'<text x="{bx:.2f}" y="{by:.2f}" font-size="2.6" font-weight="700" '
                     f'fill="{color}" text-anchor="middle" font-family="Helvetica,Arial">{esc(f["ref"])}</text>')
        val = f["value"][:16]
        vw = text_w(val, 2.0)
        if vw <= w - 0.8 and h >= 2.6:  # value fits inside the body box
            o.append(f'<text x="{lx:.2f}" y="{sy + h/2 + 0.7:.2f}" font-size="2.0" font-weight="600" '
                     f'fill="{color}" text-anchor="middle" font-family="Helvetica,Arial">{esc(val)}</text>')
        else:
            vy, ok = place(lx, y1 - mny + 2.0, val, 2.0, (0, +2.7, -2.7))
            if ok:
                o.append(f'<text x="{lx:.2f}" y="{vy:.2f}" font-size="2.0" fill="{color}" '
                         f'text-anchor="middle" font-family="Helvetica,Arial">{esc(val)}</text>')
            else:
                bx, row = band_slot(lx, val, 2.0, "bot")
                by = H + 3.2 + row * 3.1
                placed.append((bx - text_w(val, 2.0)/2, by - 2.0, bx + text_w(val, 2.0)/2, by + 0.3))
                o.append(f'<line x1="{lx:.2f}" y1="{sy + h:.2f}" x2="{bx:.2f}" y2="{by - 1.7:.2f}" '
                         f'stroke="{color}" stroke-width="0.15"/>')
                o.append(f'<text x="{bx:.2f}" y="{by:.2f}" font-size="2.0" '
                         f'fill="{color}" text-anchor="middle" font-family="Helvetica,Arial">{esc(val)}</text>')
    return "\n".join(o)

# ---------------- BOM ----------------
def bom_rows(fps):
    groups = {}
    order = []
    for f in fps:
        if f["ref"].startswith("MH"): continue
        key = (f["value"], f["pkg"])
        if key not in groups:
            groups[key] = dict(value=f["value"], pkg=f["pkg"], refs=[], tht=f["tht"], pads=f["pads"])
            order.append(key)
        groups[key]["refs"].append(f["ref"])
    rows = []
    for k in order:
        g = groups[k]
        cls, color = classify(dict(ref=g["refs"][0], value=g["value"], pkg=g["pkg"]))
        pol = ""
        padnums = {p["num"].upper() for p in g["pads"]}
        if cls == "d" and (padnums & {"K", "CATHODE"}): pol = "K = cathode (bar mark)"
        elif cls == "led": pol = "match cathode notch / pad-1 dot"
        elif cls == "u": pol = "pin 1 = dot"
        rows.append(dict(refs=" ".join(g["refs"]), value=g["value"], pkg=g["pkg"],
                         side="F", mount="THT" if g["tht"] else "SMD",
                         cls=cls, color=color, pol=pol, qty=len(g["refs"])))
    # sort: solder order (profile): R, D/LED, U, C, L, J, F
    prio = {"r": 0, "d": 1, "led": 2, "u": 3, "c": 4, "l": 5, "f": 6, "j": 7, "x": 8}
    rows.sort(key=lambda r: (prio.get(r["cls"], 9), r["refs"]))
    return rows

# ---------------- page assembly ----------------
def board_page(n, subtitle):
    pcb, fps, bb = load_board(n)
    svgp = SVGDIR / f"board{n}.svg"
    s = svgp.read_text()
    W, H = (float(x) for x in re.search(r'viewBox="[\d.]+ [\d.]+ ([\d.]+) ([\d.]+)"', s).groups())
    silks = svg_texts(svgp)
    conv, err = pick_rotation_conv(fps, silks, bb)
    assert err < 2.0, f"board{n}: rotation convention check failed (err={err:.2f}mm)"
    assert abs((bb[2]-bb[0]) - W) < 0.5 and abs((bb[3]-bb[1]) - H) < 0.5, \
        f"board{n}: Edge_Cuts bbox {bb} != SVG {W}x{H}"
    assert err < 2.0, f"board{n}: rotation convention check failed (err={err:.2f}mm)"
    inner = s[s.find("<g "):s.rfind("</svg>")]
    PADX, PADY = 12, 13
    ov = overlay(fps, conv, bb, W, H)
    rows = bom_rows(fps)
    ncomp = sum(r["qty"] for r in rows)
    dense = ' dense' if len(rows) > 16 else ''

    tr = "".join(
        f'<tr><td><span class="chip" style="background:{r["color"]}"></span></td>'
        f'<td>{html.escape(r["refs"])}</td><td><b>{html.escape(r["value"])}</b></td>'
        f'<td>{html.escape(r["pkg"])}</td><td>{r["mount"]}</td><td>{r["qty"]}</td>'
        f'<td>{r["pol"]}</td></tr>'
        for r in rows)

    return f"""
<div class="page{dense}">
  <div class="hdr"><div>
    <h2>aquarium v0 — Component Placement · Board {n}</h2>
    <p class="sub">{html.escape(subtitle)} &nbsp;·&nbsp; {W:.1f} × {H:.1f} mm &nbsp;·&nbsp;
    {ncomp} components + mounting holes &nbsp;·&nbsp; TOP (component) side view, all parts on FRONT</p>
  </div><div class="legend">
    {''.join(f'<span><i style="background:{c}"></i>{CLS_NAME[k]}</span>'
             for k, c in [("u","#d92b2b"),("d","#e07800"),("led","#c9a300"),("r","#44586e"),
                          ("c","#1f61c4"),("l","#148a4c"),("j","#8a5a2b"),("f","#b23db2")]
             if any(row["cls"] == k for row in rows))}
  </div></div>

  <div class="dwg">
  <svg viewBox="{-PADX} {-PADY} {W + 2*PADX} {H + 2*PADY}" xmlns="http://www.w3.org/2000/svg">
    {inner}
    {ov}
  </svg>
  </div>

  <table>
    <thead><tr><th></th><th>Refs</th><th>Value</th><th>Package</th><th>Mount</th><th>Qty</th><th>Polarity / note</th></tr></thead>
    <tbody>{tr}</tbody>
  </table>
  <p class="foot">Diagram is a guide — the board's own silkscreen is authoritative. ● = pin 1 ·
  K + bar = diode cathode · dashed box = LED. Table rows are in suggested soldering order
  (low-profile parts first, LEDs &amp; connectors last). Not to scale — print is enlarged for readability.</p>
</div>"""

def cover():
    return """
<div class="page cover">
  <h1>aquarium v0 — PCB Assembly Pack</h1>
  <p class="sub">Component placement diagrams for the 4-board 24 V LED driver panel (fab rev Sep 2026)</p>
  <div class="covgrid">
    <div>
      <h3>Boards (snap apart from panel first)</h3>
      <ol>
        <li><b>Board 1</b> — 150.5 × 20 mm — input: 24V IN → fuse → switch, ESP32 header</li>
        <li><b>Board 2</b> — 149.0 × 20 mm — RED + BLUE channels</li>
        <li><b>Board 3</b> — 97.9 × 20 mm — W3 channel</li>
        <li><b>Board 4</b> — 175.1 × 20 mm — DEEP-RED + W4 channels</li>
      </ol>
      <h3>Before you solder</h3>
      <ul>
        <li>All components go on the <b>front</b> (the side with the white "AQUARIUM V0 DRIVER" text).</li>
        <li>Each page's table lists parts in <b>soldering order</b>: resistors → diodes → ICs →
            capacitors → inductors → fuse → connectors last.</li>
        <li>Polarity parts: SS310 diodes (K bar), LEDs (dashed box — check datasheet notch),
            AL8860 (pin-1 dot), electrolytics. Everything else is orientation-free.</li>
        <li>Work one table row at a time; tick refs off as you go.</li>
        <li>After each board: continuity-check fuse → switch → driver inputs before LEDs.</li>
      </ul>
    </div>
    <div>
      <h3>How to read the diagrams</h3>
      <ul>
        <li>Coloured box = component body location; label above = reference, below = value.</li>
        <li>● dot = pin 1. &nbsp;K + bar = diode cathode. &nbsp;Dashed box = LED.</li>
        <li>Grey artwork = the actual copper / silkscreen of the board (true geometry,
            exported from the fabbed layout).</li>
      </ul>
      <h3>Print</h3>
      <ul>
        <li>A4 landscape, 100% scale — but diagrams are enlarged views, only the
            <i>board outline check</i> needs true scale (use the existing print pack for that).</li>
        <li>One board per page, 5 pages total.</li>
      </ul>
    </div>
  </div>
</div>"""

CSS = """
@page { size: A4 landscape; margin: 9mm; }
* { box-sizing: border-box; }
body { font-family: Helvetica, Arial, sans-serif; color: #111; margin: 0; }
.page { page-break-after: always; padding: 2mm 0; }
.page:last-child { page-break-after: auto; }
h1 { font-size: 17pt; margin: 6mm 0 1mm; }
h2 { font-size: 13pt; margin: 0 0 1mm; }
h3 { font-size: 10.5pt; margin: 4mm 0 1.5mm; }
.sub { font-size: 8.5pt; color: #444; margin: 0; }
.hdr { display: flex; justify-content: space-between; align-items: flex-start; gap: 6mm; }
.legend { font-size: 7.5pt; text-align: right; line-height: 1.7; white-space: nowrap; }
.legend i { display: inline-block; width: 3.2mm; height: 3.2mm; border-radius: 0.6mm;
            margin: 0 1.2mm 0 3mm; vertical-align: middle; border: 0.3mm solid #0003; }
.dwg { margin: 3mm 0; }
.dwg svg { width: 100%; max-height: 54mm; height: auto; background: white; }
table { width: 100%; border-collapse: collapse; font-size: 7.2pt; }
th, td { border: 0.3mm solid #bbb; padding: 0.7mm 1.4mm; text-align: left; }
th { background: #eee; font-size: 7.5pt; }
td:nth-child(6), th:nth-child(6) { text-align: center; }
.chip { display: inline-block; width: 3.5mm; height: 3.5mm; border-radius: 0.7mm;
        border: 0.3mm solid #0004; vertical-align: middle; }
.foot { font-size: 7pt; color: #555; margin: 1.8mm 0 0; }
.dense table { font-size: 6.6pt; }
.dense th, .dense td { padding: 0.45mm 1.2mm; }
.dense .dwg svg { max-height: 46mm; }
.dense .foot { font-size: 6.4pt; margin-top: 1mm; }
.cover .covgrid { display: grid; grid-template-columns: 1fr 1fr; gap: 10mm; margin-top: 6mm; }
.cover li, .cover p { font-size: 9.5pt; line-height: 1.5; }
@media screen { body { background:#f2f2f2; } .page { background:white; max-width:270mm;
  margin:6mm auto; padding:6mm 8mm; min-height:190mm; box-shadow:0 1mm 3mm #0002; } }
"""

def main():
    pages = [cover()] + [board_page(n, sub) for n, sub in BOARDS]
    doc = ("<!doctype html><html><head><meta charset='utf-8'>"
           "<title>aquarium v0 — PCB assembly diagrams</title>"
           f"<style>{CSS}</style></head><body>{''.join(pages)}</body></html>")
    out = HERE / "assembly_diagram.html"
    out.write_text(doc)
    print(f"wrote {out} ({out.stat().st_size//1024} KB)")

if __name__ == "__main__":
    main()
