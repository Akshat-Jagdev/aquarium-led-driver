#!/usr/bin/env python3
"""Verify aquarium_v0.kicad_sch netlist connectivity against the audited design."""
import re
import sys

NET = r"\netlist.net".replace("\\", "\\")  # placeholder, replaced below
NET = __file__.rsplit("\\", 1)[0] + r"\netlist.net"

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


# --- power rails -------------------------------------------------------
# Polarity pinout (FIXED 2026-09-09, matches KiCad footprint pad conventions):
#   D_SMA pad 1 = cathode  -> SS3100 pin 1 on +24V, pin 2 (anode) on SW.
#   CP_Radial pad 1 = "+"  -> C2 pin 1 on +24V, pin 2 on GND.
netchk("+24V",
       [("J7", "2"), ("C1", "2"), ("C2", "1"), ("U8", "1")]
       + [(f"U{i}", "5") for i in range(1, 8)]        # AL8860WT VIN
       + [(f"D{i}", "1") for i in range(1, 8)]        # SS3100 cathode
       + [(f"R{i}", "2") for i in range(10, 17)]      # RSET tops (high side)
       + [(f"C{i}", "2") for i in range(10, 17)]      # 22uF tops
       + [(f"C{i}", "2") for i in range(20, 27)])     # 100n tops
netchk("GND",
       [("J1", "2"), ("J6", "5"), ("U8", "2"), ("U8", "4"), ("U9", "1"),
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
                 ("U1", "3"), ("U2", "3"), ("U3", "3"), ("U4", "3")])
check("CTRL_R", [("R2", "1"), ("R6", "2"), ("U5", "3")])
check("CTRL_B", [("R3", "1"), ("R7", "2"), ("U6", "3")])
check("CTRL_DR", [("R4", "1"), ("R8", "2"), ("U7", "3")])

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
check("R_A", [("J2", "3"), ("R14", "1"), ("U5", "4")])
check("R_K", [("J5", "4"), ("L5", "2")])
check("B_A", [("J2", "5"), ("R15", "1"), ("U6", "4")])
check("B_K", [("J3", "6"), ("L6", "2")])
check("DR_A", [("J4", "5"), ("R16", "1"), ("U7", "4")])
check("DR_K", [("J5", "6"), ("L7", "2")])

# colour series chains (driver-PCB joins)
check("R_J23", [("J2", "4"), ("J3", "3")])
check("R_J34", [("J3", "4"), ("J4", "3")])
check("R_J45", [("J4", "4"), ("J5", "3")])
check("B_J23", [("J2", "6"), ("J3", "5")])
check("DR_J45", [("J4", "6"), ("J5", "5")])

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