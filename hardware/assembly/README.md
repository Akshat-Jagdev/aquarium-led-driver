# Assembly diagrams — aquarium v0 driver boards

Printable component-placement pack for the 4-board 24 V driver panel.

| File | What |
|------|------|
| `assembly_diagram.pdf` | **Print this** — 5 pages, A4 landscape (cover + one page per board) |
| `assembly_diagram.html` | Same content; re-render in browser if you want to tweak |
| `gen_assembly.py` | Generator — parses `kicad_project/aquarium_v0_board{1..4}.kicad_pcb`, embeds true-geometry artwork from `svg/`, overlays labels + BOM |
| `svg/board{1..4}.svg` | kicad-cli exports (F.Cu + F.Paste + F.SilkS + Edge.Cuts) of the fabbed layout |

Regenerate after any board edit:

```sh
KC=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
cd svg && for b in 1 2 3 4; do $KC pcb export svg --mode-single \
  --layers F.Cu,F.Paste,F.SilkS,Edge.Cuts --page-size-mode 2 \
  --exclude-drawing-sheet --drill-shape-opt 2 -o board$b.svg \
  ../../kicad_project/aquarium_v0_board$b.kicad_pcb; done && cd ..
python3 gen_assembly.py
```

## Reading the pages

- Grey artwork = real copper/silk of the fabbed board; colored box = component body.
- Label above box (or in the callout band, connected by a leader line) = reference;
  value inside/below the box. Colors per legend, table lists parts in **solder order**.
- ● dot = pin 1 · **K** + bar = diode cathode · dashed box = LED.
- All parts mount on the FRONT. Board silkscreen is authoritative if in doubt.
- Boards: 1 input/ESP32 (150.5 mm) · 2 red+blue (149.0) · 3 W3 (97.9) · 4 deep-red+W4 (175.1).
  Snap the panel apart at the mouse bites before stuffing.
