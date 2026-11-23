#!/usr/bin/env python3
"""check_print_copies.py — verify the translated print copies.

Run with the KiCad bundled python:
  "C:/Users/Akshat Jagdev/AppData/Local/Programs/KiCad/10.0/bin/python.exe" \
      check_print_copies.py

Checks, per board, that `../pcb_print_pack/src/board{N}_print.kicad_pcb`
is the source board translated by exactly (8-x0, 8) with nothing else
changed, and that every drawing stays inside the translated outline:
  1. footprint sets identical, every pad + footprint origin shifted by
     exactly (dx, dy), rotations unchanged
  2. track counts identical, every segment start/end and via shifted
  3. zone counts identical, filled areas unchanged (fills moved with
     their outlines, no refill needed)
  4. Edge.Cuts outline min lands at (8, 8)
  5. no drawing item (silk, courtyards excluded) outside the outline
     window — catches any untranslated top-level graphics token
"""
import os
import sys

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", "pcb_print_pack", "src"))

WINDOWS = {1: (0.0, 0.0), 2: (151.0, 0.0), 3: (300.5, 0.0), 4: (398.9, 0.0)}
WIDTHS = {1: 150.5, 2: 149.0, 3: 97.9, 4: 175.1}
MARGIN = 8.0

fails = []


def bad(msg):
    fails.append(msg)


def shifted(a, b, dx, dy, what):
    ax, ay = a.x / 1e6, a.y / 1e6
    bx, by = b.x / 1e6, b.y / 1e6
    if abs((bx - ax) - dx) > 1e-4 or abs((by - ay) - dy) > 1e-4:
        bad(f"{what}: delta ({bx-ax:.4f},{by-ay:.4f}) != ({dx},{dy})")


for n, (x0, y0) in sorted(WINDOWS.items()):
    dx, dy = MARGIN - x0, MARGIN - y0
    base = pcbnew.LoadBoard(os.path.join(HERE, f"aquarium_v0_board{n}.kicad_pcb"))
    copy = pcbnew.LoadBoard(os.path.join(SRC, f"board{n}_print.kicad_pcb"))

    b_refs = {fp.GetReference(): fp for fp in base.GetFootprints()}
    c_refs = {fp.GetReference(): fp for fp in copy.GetFootprints()}
    if set(b_refs) != set(c_refs):
        bad(f"B{n} footprint sets differ")
        continue
    for ref in sorted(b_refs):
        bp, cp = b_refs[ref], c_refs[ref]
        shifted(bp.GetPosition(), cp.GetPosition(), dx, dy, f"B{n} {ref} origin")
        if abs(bp.GetOrientation().AsDegrees()
               - cp.GetOrientation().AsDegrees()) > 1e-6:
            bad(f"B{n} {ref} rotation changed")
        bps, cps = list(bp.Pads()), list(cp.Pads())
        if len(bps) != len(cps):
            bad(f"B{n} {ref} pad count differs")
            continue
        for bpd, cpd in zip(bps, cps):
            shifted(bpd.GetPosition(), cpd.GetPosition(), dx, dy,
                    f"B{n} {ref} pad {bpd.GetPadName()}")

    bseg = [t for t in base.GetTracks() if t.Type() != pcbnew.PCB_VIA_T]
    cseg = [t for t in copy.GetTracks() if t.Type() != pcbnew.PCB_VIA_T]
    bvia = [t for t in base.GetTracks() if t.Type() == pcbnew.PCB_VIA_T]
    cvia = [t for t in copy.GetTracks() if t.Type() == pcbnew.PCB_VIA_T]
    if len(bseg) != len(cseg) or len(bvia) != len(cvia):
        bad(f"B{n} track counts differ")
    for bv, cv in zip(bvia, cvia):
        shifted(bv.GetPosition(), cv.GetPosition(), dx, dy, f"B{n} via")
    for bs, cs in zip(bseg, cseg):
        shifted(bs.GetStart(), cs.GetStart(), dx, dy, f"B{n} segment start")
        shifted(bs.GetEnd(), cs.GetEnd(), dx, dy, f"B{n} segment end")

    bz, cz = list(base.Zones()), list(copy.Zones())
    if len(bz) != len(cz):
        bad(f"B{n} zone count {len(bz)} vs {len(cz)}")
    for zb, zc in zip(bz, cz):
        if abs(zb.GetFilledArea() - zc.GetFilledArea()) > 1e4:
            bad(f"B{n} zone filled area changed")

    # outline: exact gr_line endpoints, min -> (8,8), span -> W x 20
    xs, ys = [], []
    for e in copy.GetDrawings():
        if e.GetLayer() == pcbnew.Edge_Cuts:
            for p in (e.GetStart(), e.GetEnd()):
                xs.append(p.x / 1e6)
                ys.append(p.y / 1e6)
    if abs(min(xs) - MARGIN) > 1e-3 or abs(min(ys) - MARGIN) > 1e-3:
        bad(f"B{n} outline min ({min(xs)},{min(ys)}) != ({MARGIN},{MARGIN})")
    if abs((max(xs) - min(xs)) - WIDTHS[n]) > 1e-3 or abs(max(ys) - min(ys) - 20) > 1e-3:
        bad(f"B{n} outline span {(max(xs)-min(xs)):.3f}x{(max(ys)-min(ys)):.3f}"
            f" != {WIDTHS[n]}x20")

    # every top-level drawing on any layer inside the window (courtyard
    # overhang at joint headers is footprint-internal and excluded here;
    # top-level graphics have no business off-board)
    for e in copy.GetDrawings():
        if e.GetLayer() == pcbnew.Edge_Cuts:
            continue
        bb = e.GetBoundingBox()
        x0m, y0m = bb.GetX() / 1e6, bb.GetY() / 1e6
        x1m = (bb.GetX() + bb.GetWidth()) / 1e6
        y1m = (bb.GetY() + bb.GetHeight()) / 1e6
        if (x0m < MARGIN - 0.1 or x1m > MARGIN + WIDTHS[n] + 0.1
                or y0m < MARGIN - 0.1 or y1m > MARGIN + 20 + 0.1):
            bad(f"B{n} drawing {e.Type()} escapes window "
                f"x[{x0m:.2f},{x1m:.2f}] y[{y0m:.2f},{y1m:.2f}]")

    print(f"B{n}: {len(b_refs)} fps, {len(bps) and len(b_refs)} checked, "
          f"{len(bseg)} segs, {len(bvia)} vias, {len(bz)} zones — "
          f"outline ({min(xs)},{min(ys)})..({max(xs)},{max(ys)})")

if fails:
    for f in fails:
        print("FAIL:", f)
    sys.exit(1)
print("PRINT-COPY CHECK: ALL PASS")