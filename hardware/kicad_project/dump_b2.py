#!/usr/bin/env python3
"""One-off: dump board 2 pad geometry (abs coords) + vias + zone rects."""
import math
import re

SRC = open("aquarium_v0_board2.kicad_pcb", encoding="utf-8").read()

starts = [m.start() for m in re.finditer(r"\n\t\(footprint ", SRC)]
starts.append(len(SRC))
for i in range(len(starts) - 1):
    blk = SRC[starts[i]:starts[i + 1]]
    mref = re.search(r'\(property "Reference" "([^"]+)"', blk)
    ref = mref.group(1) if mref else "?"
    mat = re.search(r"\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)", blk)
    fx, fy = float(mat.group(1)), float(mat.group(2))
    rot = float(mat.group(3) or 0.0)
    print("=== %s at (%.4f, %.4f) rot %.1f" % (ref, fx, fy, rot))
    for chunk in blk.split("\n\t\t(pad ")[1:]:
        head = chunk[:400]
        mp = re.match(r'"([^"]+)" (\w+) (\w+)\s*\(at ([-\d.]+) ([-\d.]+)(?: '
                      r'([-\d.]+))?\)\s*\(size ([-\d.]+) ([-\d.]+)\)', head)
        if not mp:
            print("  ?? unparsed pad head:", head[:80].replace("\n", " "))
            continue
        mnet = re.search(r'\(net "([^"]*)"\)', head)
        mdrill = re.search(r'\(drill ([\d.]+)\)', head)
        pn = mp.group(1)
        px, py = float(mp.group(4)), float(mp.group(5))
        prot = float(mp.group(6) or 0)
        sw, sh = float(mp.group(7)), float(mp.group(8))
        net = mnet.group(1) if mnet else "NONE"
        r = math.radians(rot + prot)
        ax = fx + px * math.cos(r) - py * math.sin(r)
        ay = fy + px * math.sin(r) + py * math.cos(r)
        print("  p%-3s (%9.4f,%9.4f) %6.3f x %-6.3f drill %-4s net %s"
              % (pn, ax, ay, sw, sh, mdrill.group(1) if mdrill else "-", net))

print("=== vias ===")
for chunk in SRC.split("\n\t(via\n")[1:]:
    head = chunk[:300]
    mv = re.match(r'\s*\(at ([-\d.]+) ([-\d.]+)\)\s*\(size ([\d.]+)\)\s*'
                   r'\(drill ([\d.]+)\)', head)
    mnet = re.search(r'\(net "([^"]*)"\)', head)
    if mv:
        print("  via net %-12s (%9.4f,%9.4f) size %s drill %s"
              % (mnet.group(1) if mnet else "?", float(mv.group(1)),
                 float(mv.group(2)), mv.group(3), mv.group(4)))

print("=== zone net + first pts ===")
for mz in re.finditer(r'\(zone \(net "([^"]*)"\)', SRC):
    zblk = SRC[mz.start():mz.start() + 1500]
    pts = re.findall(r"\(xy ([\d.]+) ([\d.]+)\)", zblk)[:6]
    print("  zone %-8s %s" % (mz.group(1), pts))