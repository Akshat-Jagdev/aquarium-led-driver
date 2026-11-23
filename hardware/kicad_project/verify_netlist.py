#!/usr/bin/env python3
"""Verify aquarium_v0.kicad_sch netlist connectivity against the audited design."""
import re
import sys

import os
NET = os.path.join(os.path.dirname(os.path.abspath(__file__)), "netlist.net")

text = open(NET, encoding="utf-8").read()

# parse nets — KiCad 10 writes tab-indented s-expr:
# (net\n\t\t\t(code "x")\n\t\t\t(name "n") ... (node\n\t\t\t\t\t(ref "R")\n\t\t\t\t\t(pin "p"))\n\t\t)
nets = {}
for m in re.finditer(
        r'\(net\s+\(code "[^"]*"\)\s*\(name "([^"]*)"\)(.*?)\n\t\t\)',
        text, re.S):
    name, body = m.group(1), m.group(2)
    nodes = set()
    for nm in re.finditer(
            r'\(node\s*\(ref "([^"]*)"\)\s*\(pin "([^"]*)"\)', body):
        nodes.add((nm.group(1), nm.group(2)))
    nets[name] = nodes

def norm(n):
    return n.lstrip("/")

nets = {norm(k): v for k, v in nets.items()}
print(f"nets parsed: {len(nets)}")

fails = []


def check(netname, expected):
    got = nets.get(netname, set())
    exp = set(expected)
    missing = exp - got
    extra = got - exp
    if got != exp:
        fails.append(
            f"{netname}: missing={sorted(missing)} extra={sorted(extra)}")
    else:
        print(f"  ok {netname} ({len(exp)} nodes)")


def netchk(netname, must):
    got = nets.get(netname, set())
    miss = set(must) - got
    if miss:
        fails.append(f"{netname}: MISSING {sorted(miss)}")
    else:
        print(f"  ok {netname} contains all {len(set(must))} required nodes")


# --- power rails (dual rail since the 2026-09-14 audit fix) -------------
# Rail A +24V: white channels (U1-U4) + logic input.
# Rail B +12V: U10 LM2596 pre-regulator -> red/blue/660nm (U5-U7).
# Polarity pinout (FIXED 2026-09-09, matches KiCad footprint pad conventions):
#   D_SMA pad 1 = cathode  -> SS3100 pin 1 on the channel rail, pin 2 (anode) on SW.
#   CP_Radial pad 1 = "+"  -> C2 pin 1 on +24V, pin 2 on GND.
netchk("+24V",
       [("J7", "2"), ("C1", "2"), ("C2", "1"), ("U8", "1"), ("U10", "1")]
       + [(f"U{i}", "5") for i in range(1, 5)]        # white AL8860WT VIN
       + [(f"D{i}", "1") for i in range(1, 5)]        # white SS3100 cathode
       + [(f"R{i}", "2") for i in range(10, 14)]      # white RSET tops
       + [(f"C{i}", "2") for i in range(10, 14)]      # white 22uF tops
       + [(f"C{i}", "2") for i in range(20, 24)])     # white 100n tops
netchk("+12V",
       [("U10", "3"), ("C12V", "2")]
       + [(f"U{i}", "5") for i in range(5, 8)]        # colour AL8860WT VIN
       + [(f"D{i}", "1") for i in range(5, 8)]        # colour SS3100 cathode
       + [(f"R{i}", "2") for i in range(14, 17)]      # colour RSET tops
       + [(f"C{i}", "2") for i in range(14, 17)]      # colour 22uF tops
       + [(f"C{i}", "2") for i in range(24, 27)])     # colour 100n tops
netchk("GND",
       [("J1", "2"), ("J6", "5"), ("U8", "2"), ("U8", "4"), ("U9", "1"),
        ("U10", "2"), ("U10", "4"), ("C12V", "1"),
        ("C3", "1"), ("C4", "1"), ("C1", "1"), ("C2", "2")]
       + [(f"U{i}", "2") for i in range(1, 8)]        # AL8860WT GND
       + [(f"R{i}", "1") for i in range(5, 9)]        # 100k bottoms
       + [(f"C{i}", "1") for i in range(10, 17)]
       + [(f"C{i}", "1") for i in range(20, 27)])
check("+5V", [("U8", "3"), ("C3", "2"), ("U9", "3")])
check("+3V3", [("U9", "2"), ("C4", "2"), ("J6", "6")])
check("VIN_RAW", [("J1", "1"), ("F1", "1")])
check("SW_A", [("F1", "2"), ("J7", "1")])

# --- control ----------------------------------------------------------
check("PWM_W", [("J6", "1"), ("R1", "2")])
check("PWM_R", [("J6", "2"), ("R2", "2")])
check("PWM_B", [("J6", "3"), ("R3", "2")])
check("PWM_DR", [("J6", "4"), ("R4", "2")])
check("CTRL_W", [("R1", "1"), ("R5", "2"),
                 ("U1", "3"), ("U2", "3"), ("U3", "3"), ("U4", "3")]
      + [(ref, "5") for ref in ("J8", "J9", "J10", "J11", "J12", "J13")])
check("CTRL_R", [("R2", "1"), ("R6", "2"), ("U5", "3"),
                 ("J8", "7"), ("J9", "7")])
check("CTRL_B", [("R3", "1"), ("R7", "2"), ("U6", "3"),
                 ("J8", "6"), ("J9", "6")])
check("CTRL_DR", [("R4", "1"), ("R8", "2"), ("U7", "3"),
                  ("J8", "8"), ("J9", "8"),
                  ("J10", "6"), ("J11", "6"), ("J12", "6"), ("J13", "6")])

# --- channels: switching node + string nets ---------------------------
# AL8860WT-7 (DS39014): 1=SW 2=GND 3=CTRL 4=SET 5=VIN.
# {net}_A = string anode = RSET bottom = SET pin (high-side sense).
# {net}_K = string cathode = inductor top; L bottom sits on the SW node.
CH = [("U1", "L1", "D1", "R10", "W1_A", "W1_K", "J2"),
      ("U2", "L2", "D2", "R11", "W2_A", "W2_K", "J3"),
      ("U3", "L3", "D3", "R12", "W3_A", "W3_K", "J4"),
      ("U4", "L4", "D4", "R13", "W4_A", "W4_K", "J5"),
      ("U5", "L5", "D5", "R14", "R_A", "R_K", "J2"),
      ("U6", "L6", "D6", "R15", "B_A", "B_K", "J2"),
      ("U7", "L7", "D7", "R16", "DR_A", "DR_K", "J4")]
for (u, l, d, r, a, k, hdr) in CH:
    # SW node: IC pin1 + L pin1 + D anode (pin 2; pad 1 = cathode)
    sw_nodes = [(u, "1"), (l, "1"), (d, "2")]
    hit = [n for n, nodes in nets.items()
           if n not in ("+24V", "GND", "+5V", "+3V3") and set(sw_nodes) <= nodes]
    if len(hit) != 1:
        fails.append(f"SW node of {u}: found nets {hit}")
    else:
        print(f"  ok SW({u}) net '{hit[0]}'")

# header / string nets: A = anode (SET + RSET bottom + header pin1),
#                      K = cathode (inductor top + header pin2)
check("W1_A", [("J2", "1"), ("R10", "1"), ("U1", "4")])
check("W1_K", [("J2", "2"), ("L1", "2")])
check("W2_A", [("J3", "1"), ("R11", "1"), ("U2", "4")])
check("W2_K", [("J3", "2"), ("L2", "2")])
check("W3_A", [("J4", "1"), ("R12", "1"), ("U3", "4")])
check("W3_K", [("J4", "2"), ("L3", "2")])
check("W4_A", [("J5", "1"), ("R13", "1"), ("U4", "4")])
check("W4_K", [("J5", "2"), ("L4", "2")])
check("R_A", [("J2", "3"), ("R14", "1"), ("U5", "4"),
              ("J8", "10"), ("J9", "10")])
check("R_K", [("J5", "4"), ("L5", "2"),
              ("J10", "8"), ("J11", "8"), ("J12", "9"), ("J13", "9")])
check("B_A", [("J2", "5"), ("R15", "1"), ("U6", "4"),
              ("J8", "9"), ("J9", "9")])
check("B_K", [("J3", "6"), ("L6", "2")])
check("DR_A", [("J4", "5"), ("R16", "1"), ("U7", "4"),
               ("J12", "10"), ("J13", "10")])
check("DR_K", [("J5", "6"), ("L7", "2")])

# colour series chains (now joined via the board-joint harnesses)
check("R_J23", [("J2", "4"), ("J3", "3"), ("J8", "12"), ("J9", "12")])
check("R_J34", [("J3", "4"), ("J4", "3"), ("J10", "7"), ("J11", "7")])
check("R_J45", [("J4", "4"), ("J5", "3"), ("J12", "7"), ("J13", "7")])
check("B_J23", [("J2", "6"), ("J3", "5"), ("J8", "11"), ("J9", "11")])
check("DR_J45", [("J4", "6"), ("J5", "5"), ("J12", "8"), ("J13", "8")])

# --- board joint headers (4-board split, 2026-09-10) --------------------
# Pin maps identical at both ends of each seam. Seam 1 = 1x12,
# seams 2-3 = 1x10; NC pins must NOT carry a real net.
JOINT_PIN_NETS = {
    "J8":  {1: "+24V", 2: "+12V", 3: "GND", 4: "GND",
            5: "CTRL_W", 6: "CTRL_B", 7: "CTRL_R", 8: "CTRL_DR",
            9: "B_A", 10: "R_A", 11: "B_J23", 12: "R_J23"},
    "J9":  {1: "+24V", 2: "+12V", 3: "GND", 4: "GND",
            5: "CTRL_W", 6: "CTRL_B", 7: "CTRL_R", 8: "CTRL_DR",
            9: "B_A", 10: "R_A", 11: "B_J23", 12: "R_J23"},
    "J10": {1: "+24V", 2: "+12V", 3: "GND", 4: "GND",
            5: "CTRL_W", 6: "CTRL_DR", 7: "R_J34", 8: "R_K",
            9: None, 10: None},
    "J11": {1: "+24V", 2: "+12V", 3: "GND", 4: "GND",
            5: "CTRL_W", 6: "CTRL_DR", 7: "R_J34", 8: "R_K",
            9: None, 10: None},
    "J12": {1: "+24V", 2: "+12V", 3: "GND", 4: "GND",
            5: "CTRL_W", 6: "CTRL_DR", 7: "R_J45", 8: "DR_J45",
            9: "R_K", 10: "DR_A"},
    "J13": {1: "+24V", 2: "+12V", 3: "GND", 4: "GND",
            5: "CTRL_W", 6: "CTRL_DR", 7: "R_J45", 8: "DR_J45",
            9: "R_K", 10: "DR_A"},
}
joint_node_map = {}                       # netname -> {(ref,pin)...}
for ref, pinmap in JOINT_PIN_NETS.items():
    for pin, netname in pinmap.items():
        if netname is None:
            un = f"unconnected-({ref}-Pad{pin})"
            if un not in nets:
                fails.append(f"joint {ref} pin {pin}: expected NC, "
                             f"net '{un}' missing")
        else:
            joint_node_map.setdefault(netname, set()).add((ref, str(pin)))
for netname, nodes in joint_node_map.items():
    got = nets.get(netname, set())
    miss = nodes - got
    if miss:
        fails.append(f"joint map {netname}: MISSING {sorted(miss)}")
    else:
        print(f"  ok joint map {netname} "
              f"({len(nodes)} joint pins present)")

# --- single-node nets (would indicate a label typo) --------------------
# KiCad's own "unconnected-(...)" nets (no_connect pins) are expected.
loners = [n for n, nodes in nets.items()
          if len(nodes) < 2 and not n.startswith("unconnected-")]
if loners:
    fails.append(f"single-node nets: {loners}")

print()
if fails:
    print("FAILURES:")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("ALL CONNECTIVITY CHECKS PASSED")