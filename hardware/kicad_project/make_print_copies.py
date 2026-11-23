#!/usr/bin/env python3
"""make_print_copies.py — translated print/fab copies of the 4 boards.

kicad-cli pdf/svg export plots at ABSOLUTE board coordinates on the page
(`(paper "A3")`, 420x297), so board 4 (x 398.9-574) hangs off the page
and boards 1-3 sit flush with the page edge. The split keeps the
original 580 mm frame on purpose (cell geometry proven), so the fab
artwork needs a translated copy to print/plot correctly.

For each board this writes `<out>/board{N}_print.kicad_pcb` with every
top-level item shifted so the board's outline min lands at (8, 8) mm,
and `(paper "A4")` so the exported PDF/SVG page is A4 (210x297 mm) —
all four boards fit at 1:1 with printable margins.

Shift rules by top-level s-expr block (child coords inside footprints
are RELATIVE to the footprint origin and are never touched):
  footprint            -> the block's own (at x y [rot])   (first (at at depth 2)
  segment              -> (start)/(end)
  via                  -> (at x y)
  arc                  -> (start)/(mid)/(end)
  gr_line/gr_rect      -> (start)/(end)
  gr_arc               -> (start)/(mid)/(end)
  gr_circle            -> (center)/(end)   (pin-1 markers at J2-J13)
  gr_poly              -> every (xy)
  gr_text              -> (at x y [rot])
  zone                 -> every (xy)  (outline AND filled_polygon pts)
Zone fills are shifted with the outline, so no refill is needed.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# per-board x/y shift: outline min -> (8, 8)
WINDOWS = {1: (0.0, 0.0), 2: (151.0, 0.0), 3: (300.5, 0.0), 4: (398.9, 0.0)}
# outline widths (Edge_Cuts x-span of the source boards)
WIDTHS = {1: 150.5, 2: 149.0, 3: 97.9, 4: 175.1}
MARGIN = 8.0

# token -> (min depth allowed, shift?) handled per context below
COORD_TOKENS = ("at", "start", "end", "mid", "pos", "xy", "center")


def fmt(v):
    s = f"{v:.6f}".rstrip("0").rstrip(".")
    return s if s not in ("", "-") else "0"


def shift_pair(m, dx, dy):
    x, y = float(m.group(2)), float(m.group(3))
    return m.group(1) + fmt(x + dx) + " " + fmt(y + dy) + m.group(4)


def translate(text, dx, dy):
    out = []
    i = 0
    depth = 0
    context = []  # block name stack; context[0] = top-level block name
    n = len(text)
    while i < n:
        c = text[i]
        if c == "(":
            m = re.match(r"\(\s*([A-Za-z_0-9]+)", text[i:])
            name = m.group(1) if m else ""
            depth += 1
            # depth 1 = root (kicad_pcb; depth 2 = top-level item ->
            # context[0]; deeper = its children.
            if depth == 2:
                context = [name]
            # decision: is the coord pair at this opener shifted?
            # (computed BEFORE appending the name — a shifted token
            # consumes its own closing paren, so it must never enter
            # the context stack)
            shift = False
            if depth >= 3 and name in COORD_TOKENS:
                top = context[0] if context else ""
                if top == "zone" and name == "xy":
                    shift = True  # outline + filled_polygon, any depth
                elif top == "gr_poly" and name == "xy":
                    shift = True
                elif depth == 3:  # direct child of the top-level item
                    if top == "footprint" and name == "at":
                        # the block's own (at is the only DIRECT (at child
                        # (pads/properties wrap theirs one level deeper)
                        shift = True
                    elif top in ("segment", "arc", "gr_line", "gr_rect",
                                 "gr_arc") and name in ("start", "end", "mid"):
                        shift = True
                    elif top == "gr_circle" and name in ("center", "end"):
                        shift = True
                    elif top == "via" and name == "at":
                        shift = True
                    elif top == "gr_text" and name == "at":
                        shift = True
            if shift:
                mm = re.match(
                    r"(\(\s*[A-Za-z_0-9]+\s+)(-?[\d.]+)\s+(-?[\d.]+)([ )])",
                    text[i:])
                if mm:
                    out.append(shift_pair(mm, dx, dy))
                    i += mm.end()
                    if mm.group(4) == ")":
                        # token fully consumed incl. close (no rotation);
                        # with a rotation the trailing ")" is still ahead
                        # in the stream and the main loop handles it
                        depth -= 1
                    continue
                print(f"WARN: unshifted coord {name!r} at offset {i}",
                      file=sys.stderr)
            if depth > 2:
                context.append(name)
            out.append(c)
            i += 1
        elif c == ")":
            depth -= 1
            if depth <= 1:
                context = []
            elif len(context) > 1:
                context.pop()
            out.append(c)
            i += 1
        else:
            out.append(c)
            i += 1
    return "".join(out)


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "print_src")
    os.makedirs(outdir, exist_ok=True)
    for n, (x0, y0) in sorted(WINDOWS.items()):
        src = os.path.join(HERE, f"aquarium_v0_board{n}.kicad_pcb")
        text = open(src, encoding="utf-8").read()
        # sanity: footprint count before/after must match
        nf = text.count("(footprint ")
        new = translate(text, MARGIN - x0, MARGIN - y0)
        assert new.count("(footprint ") == nf, "footprint count changed"
        # The board title is anchored at original x0+6 but is ~28.7 mm
        # wide, so it hangs ~8.4 mm west of the board edge and would sit
        # half off the A4 page after translation. Center it on the
        # translated outline (print copies only — the fab boards keep
        # the original silk).
        new = re.sub(
            r'(\(gr_text\s+"AQUARIUM V0 DRIVER[^"]*"\s*\(at\s+)'
            r'-?[\d.]+\s+(-?[\d.]+)',
            lambda m: m.group(1) + fmt(MARGIN + WIDTHS[n] / 2) + " "
                      + m.group(2),
            new, count=1)
        assert re.search(
            r'\(gr_text\s+"AQUARIUM V0 DRIVER[^"]*"\s*\(at\s+'
            + re.escape(fmt(MARGIN + WIDTHS[n] / 2)) + r'\s',
            new), "title not recentered"
        # paper A4 so every plot page is 210x297 mm
        new = new.replace('(paper "A3")', '(paper "A4")', 1)
        assert '(paper "A4")' in new, "paper token not found"
        dst = os.path.join(outdir, f"board{n}_print.kicad_pcb")
        with open(dst, "w", encoding="utf-8", newline="\n") as f:
            f.write(new)
        print(f"board{n}: shift ({MARGIN - x0:+g}, {MARGIN:+g}) -> {dst}")


if __name__ == "__main__":
    main()