# DIY PCB Print Pack — aquarium_v0 driver boards (4 boards)

Everything you need to make the 4 driver boards **at home** (toner
transfer or UV photoresist), generated 2026-09-12 from the verified,
DRC-clean split boards. The artwork is byte-equivalent to the fab
boards, only translated so each board sits at an 8 mm margin on an
A4 page (the fab files plot at the original 580 mm-frame coordinates
and run off the page).

```
pcb_print_pack/
├── board1/ … board4/          one folder per board
│   ├── print/                 6 printable PDFs (A4 landscape, 1:1)
│   ├── drill/                 Excellon .drl + hole-map PDF + report
│   └── gerber/                full 7-layer fab set (if you give up
│                              and send them to JLCPCB after all 😉)
└── src/                       the translated KiCad files used to plot
                               everything (open in KiCad to re-plot)
```

| Board | Size (mm) | Vias | Plated holes | Unplated (M3) |
|-------|-----------|------|--------------|----------------|
| 1 | 150.5 × 20 | 31 | 69 | 2 |
| 2 | 149.0 × 20 | 44 | 72 | 2 |
| 3 | 97.9 × 20 | 26 | 52 | 2 |
| 4 | 175.1 × 20 | 34 | 50 | 2 |

## 1. Printing — the one rule that matters

**Print at 100% / "Actual size". Never "fit to page" or "shrink
oversized pages".** Laser printer, highest resolution/darkest setting.

**Scale check (mandatory, every print):** print `boardN_Edge_Cuts.pdf`
and measure the board outline width with a steel ruler:
B1 **150.5 mm**, B2 **149.0 mm**, B3 **97.9 mm**, B4 **175.1 mm**
(±0.2 mm). If it doesn't match, your printer is scaling — fix that
before wasting copper.

## 2. Which PDF for which method

Two copper artwork files per side — the right one depends on how you
apply it:

| Method | Top copper (F.Cu) | Bottom copper (B.Cu) |
|--------|-------------------|----------------------|
| **Toner transfer** (paper laid face-down on the copper) | `boardN_F_Cu_MIRRORED.pdf` | `boardN_B_Cu_BOTTOM-SIDE.pdf` |
| **UV photoresist** (transparency laid on top of the copper) | `boardN_F_Cu_TOP-SIDE.pdf` | `boardN_B_Cu_MIRRORED.pdf` |

For photoresist, print on transparency with the **ink side facing the
board** (flip the film over after printing) so the ink touches the
resist — sharpness.

Other files:
- `boardN_F_Silkscreen.pdf` — component-placement reference. Your home
  board will have no real silkscreen: print this and keep it next to
  you while stuffing. It also shows the board title and pin-1 markers.
- `boardN_Edge_Cuts.pdf` — board outline, also your scale check.
- Ground pours are part of the copper artwork — don't "simplify" them
  away; they carry the GND net.

## 3. Drilling

Hole sizes (from `drill/drill_report.txt` / the map PDF
`boardN_print-drl_map.pdf`):

| Size | Use | Boards | Home-shop advice |
|------|-----|--------|------------------|
| 0.3 mm | signal vias | all | **See §4 — do NOT hand-drill 0.3 mm.** |
| 1.0 mm | header/component pins (J1–J13) | all | 1.0 mm carbide bit |
| 1.3 mm | fuse clips (F1) | 1 only | 1.3 mm bit |
| 3.2 mm | M3 mounting holes (NPTH) | all | 3.2 mm; use as top/bottom **alignment pins** |

Drill AFTER etching, BEFORE solder mask/assembly. Use the drill-map
PDF as your hole template; a small drill press beats a hand drill —
the board is only 20 mm wide, so mark hole centers with a center punch
first.

## 4. The vias — read this before etching

The 0.3 mm via drill is at the limit of home tooling, and a via pad is
only 0.8 mm across — **oversizing the hole to 0.6–0.8 mm eats the
whole annular ring**. The reliable home method is **through-wire vias**:

1. Drill the vias at 0.6–0.8 mm (don't try 0.3 mm).
2. Thread each via with a strand of tinned copper wire (unwrap a
   strand from stranded wire, or use resistor-lead clippings).
3. Solder BOTH sides, then snip flush.

31/44/26/34 vias on boards 1–4 — an evening of threading. There is no
via on this board you can skip: the CTRL ladder and colour chains
change layers through them.

## 5. Two-layer alignment

- Etch the top side first, then flip the SAME copper-clad board for
  the bottom.
- Use the two 3.2 mm M3 holes as registration: after etching top,
  push two 3.2 mm pins (or drill bits) through and align the bottom
  artwork/film to them before exposure/transfer.
- Boards are 20 mm wide and all vias are through-wired, so a small
  top/bottom offset (<0.3 mm) is tolerable — but check before etching,
  not after.

## 6. Honest warnings

- **Min track 0.25 mm / min clearance 0.25 mm** (signal netclass).
  Toner transfer can do this, but you need a clean, hot transfer —
  laser printer + glossy paper (or the blue PnP sheets), no inkjet.
  If 0.25 mm traces lift, stop and troubleshoot the transfer; don't
  accept broken signal traces. Power tracks are 0.5–1.0 mm — easy.
- **No solder mask**: the 2 kHz buck converters will survive hand
  soldering without mask, but avoid solder bridges on the 0603
  passives; flux generously and inspect under magnification.
- **The LED MCPCBs cannot be made at home** (aluminum core) — order
  those from a fab as before (see `bom/PARTS_LIST.md` §10.2).
- **U8, U9, C3, C4 on board 1 stay unpopulated** (V0 decision,
  ESP32 USB-powered) — etch them anyway, just don't stuff them.
- The joints between boards need J8–J13 pin headers + 3 jumper
  harnesses (see `hardware/mechanical/pcb_layout_notes.md` §3.4) —
  a home-made board is fine for this; the headers are ordinary 2.54 mm
  breakaway strip.
- If a board gets ruined, the `gerber/` folder per board is a complete
  fab set — you can always send just that board to JLCPCB.

## 7. Verification you can do at home

1. Multimeter continuity: +24V pad to each RSET pin-2, GND ring
   continuity across the pour, no +24V-to-GND shorts before the
   drivers are stuffed.
2. Eyeball every trace against `boardN_F_Silkscreen.pdf` /
   the drill map under a loupe.
3. Before full population: install only the power path on board 1
   (F1, C2, J1), apply 24 V, check the fuse and no heat.
4. Then follow TP-02 (full PCB bench test) in the test plan.

## 8. Where this came from

- Source of truth: `hardware/kicad_project/aquarium_v0_board{1..4}.kicad_pcb`
  (DRC 0/0, `verify_pcb.py --board N` ALL PASS ×4, byte-reproducible).
- These print files were generated from translated copies
  (`src/board{N}_print.kicad_pcb`, outline anchored at 8 mm on A4)
  by `hardware/kicad_project/make_print_copies.py`; the translation
  is machine-verified by `check_print_copies.py` — every pad, track,
  via and zone moved by exactly the same offset, DRC re-checked 0/0.
- Regenerate everything: run `make_print_copies.py`, then re-run the
  kicad-cli exports (see the commands in the project checklist).