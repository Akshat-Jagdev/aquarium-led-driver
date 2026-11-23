# Find where GND / +24V / +12V get shorted in aquarium_v0.kicad_sch.
# Models KiCad sheet connectivity: pins + power-symbol pins connect at their
# (x,y); wires union their endpoints; labels name the net at their position.
import re, sys
from collections import defaultdict

S = open("aquarium_v0.kicad_sch", encoding="utf-8").read()

# --- lib symbol pin offsets: name "SYM_1_1" pin defs (x y angle name num) ---
lib_pins = defaultdict(list)   # libname -> [(x, y, num)]
for m in re.finditer(r'\(symbol "([^"]+)_1_1"\n(.*?)\n\t\t\)', S, re.S):
    lname, body = m.group(1), m.group(2)
    for pm in re.finditer(r'\(pin \w+ \w+\n\t+\(at (-?\d+) (-?\d+) (\d+)\).*?'
                          r'\(name "([^"]*)"\).*?\(number "([^"]*)"', body, re.S):
        x, y, ang, nm, num = pm.groups()
        lib_pins[lname].append((int(x), int(y), num))
for m in re.finditer(r'\(symbol "([^"]+)_0_1"\n(.*?)\n\t\t\)', S, re.S):
    lname, body = m.group(1), m.group(2)
    if lname in lib_pins:
        continue
    for pm in re.finditer(r'\(pin \w+ \w+\n\t+\(at (-?\d+) (-?\d+) (\d+)\).*?'
                          r'\(name "([^"]*)"\).*?\(number "([^"]*)"', body, re.S):
        x, y, ang, nm, num = pm.groups()
        lib_pins[lname].append((int(x), int(y), num))

# --- instances: (lib_id, ref, value, x, y, rot) ---
insts = []
for m in re.finditer(r'\(symbol\n\t\t\(lib_id "([^"]+)"\)\n\t\t\(at (-?\d+) (-?\d+) (\d+)\)'
                     r'.*?\(property "Reference" "([^"]*)".*?\(property "Value" "([^"]*)"',
                     S, re.S):
    lib, x, y, rot, ref, val = m.groups()
    insts.append((lib, ref, val, int(x), int(y), int(rot)))

def rot_pt(px, py, rot):
    rot = int(rot) % 360
    if rot == 0:
        return px, py
    if rot == 90:
        return py, -px
    if rot == 180:
        return -px, -py
    return -py, px  # 270

# --- net naming per connect-point ---
# power symbols: net = value; component pins: net = (ref, pinnum)
point_net = defaultdict(list)     # (x,y) -> [descriptor]
for lib, ref, val, x, y, rot in insts:
    base = lib.split(":")[1]
    if lib.startswith("power:"):
        # power pin at symbol-local (0,0)
        px, py = rot_pt(0, 0, rot)
        point_net[(x + px, y + py)].append(("PWR", val, ref))
    else:
        for lx, ly, num in lib_pins.get(base, []):
            px, py = rot_pt(lx, -ly, rot)  # sheet = (X+sx, Y-sy) at rot 0
            point_net[(x + px, y + py)].append(("PIN", f"{ref}-{num}", val))

# --- wires ---
wires = [tuple(map(int, m.groups())) for m in
         re.finditer(r'\(wire \(pts \(xy (-?\d+) (-?\d+)\) \(xy (-?\d+) (-?\d+)\)\)', S)]

# --- labels (local + global) at positions ---
labels = [(m.group(1), int(m.group(2)), int(m.group(3))) for m in
          re.finditer(r'\((?:label|global_label) "([^"]+)" \(at (-?\d+) (-?\d+)', S)]

# --- union-find over points; wires bridge their endpoints ---
parent = {}
def find(a):
    while parent.get(a, a) != a:
        parent[a] = parent.get(parent[a], parent[a])
        a = parent[a]
    return a
def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb:
        parent[ra] = rb

for x1, y1, x2, y2 in wires:
    union((x1, y1), (x2, y2))
# wire endpoint coinciding with a pin/power point joins that pin to the wire net
for p in list(point_net):
    for x1, y1, x2, y2 in wires:
        for q in ((x1, y1), (x2, y2)):
            if p == q:
                union(p, q)

# a label at a wire endpoint or pin point names that whole group
label_groups = defaultdict(set)
for name, lx, ly in labels:
    for x1, y1, x2, y2 in wires:
        if (lx, ly) in ((x1, y1), (x2, y2)):
            label_groups[name].add(find((lx, ly)))
    if (lx, ly) in point_net:
        label_groups[name].add(find((lx, ly)))

# map each root to the power-symbol names and pin descriptors on it
root_pwr = defaultdict(set)
root_pins = defaultdict(list)
for p, ds in point_net.items():
    for kind, a, b in ds:
        if kind == "PWR":
            root_pwr[find(p)].add(a)
        else:
            root_pins[find(p)].append(a)

# report groups mixing power nets
print("=== groups containing >1 distinct power net ===")
for root, names in root_pwr.items():
    if len(names) > 1:
        pins = sorted(set(root_pins.get(root, [])))
        print("MIXED", sorted(names), "pins:", len(pins), pins[:12], "...")
        # which wires are in this group?
        wset = [(x1, y1, x2, y2) for x1, y1, x2, y2 in wires
                if find((x1, y1)) == root or find((x2, y2)) == root]
        print("  wires:", wset[:20])
        # where do the different power symbols sit?
        spots = [(p, d) for p, ds in point_net.items() for d in ds
                 if d[0] == "PWR" and find(p) == root]
        print("  pwr spots:", [(p, d[1]) for p, d in spots][:30])

print("=== label + power collisions (label name != pwr net on same group) ===")
for name, roots in label_groups.items():
    for r in roots:
        pw = root_pwr.get(r, set())
        if pw and name not in pw:
            print(f"label {name!r} sits on group with pwr {pw}")