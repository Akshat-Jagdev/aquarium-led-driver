# ROUTING BRIEF — aquarium_v0 driver strip (facts for routing agents)

Single source of geometry truth. Read fully before routing. Coordinates are
board mm, origin = left/top board edge, **y grows DOWN** (KiCad convention).
Board: 580 × 20 mm. Copper-to-edge keepout 0.3 mm. JLCPCB minima
(track/space 0.15/0.15, via 0.5/0.3) are already the DRC rules.

## Toolchain (all verified working)

- Regenerate board: `python gen_pcb.py` (reads `netlist.net`, placement is
  code; also reads `ROUTES_EXTRA.json` — YOUR overlay — see below).
  Segments/vias are emitted with net CODE only (`(net 3)`) — correct for
  KiCad 10; no post-processing of the .kicad_pcb is needed (a previous
  emitter bug writing `(net 3 "+24V")` in track/via tokens is FIXED).
  F1 quirk: its duplicate same-net clip pads share one uuid — only the
  SECOND clip of each pad number is a live connectivity node.
- DRC oracle: `"C:/Users/Akshat Jagdev/AppData/Local/Programs/KiCad/10.0/bin/kicad-cli.exe" pcb drc --format json -o drc.json aquarium_v0.kicad_pcb`
  then parse `drc.json`: `violations` (must be **0**) and `unconnected_items`
  (list of `{items: [{description: "... [/NETNAME] ..."}], ...}` — your goal:
  no entry mentioning YOUR nets).
- Pad positions: `python -c "import gen_pcb as g; print(g.pad_pos('U1','5'))"`
  → `(140.64, 9.05)`. Net of a pad: `g.COMPS['U1']['pins']['5']`.
  Courtyard bbox: `g.fp_bbox('U1')`. Placement: `g.PLACEMENT['U1']`.
  **Import gen_pcb from your scratch copy** (it self-contains everything).
- Same-net overlap with a pad is FINE (that is a connection). Different-net
  clearance is 0.15 mm (0.3 mm for netclasses Power_24V/LED_*).

## Overlay format (`ROUTES_EXTRA.json` in YOUR scratch dir only)

```json
{"routes": [{"net": "/W1_A", "layer": "F.Cu", "width": 1.0,
             "pts": [[x, y], [x, y], [x, y]]}],
 "vias":   [{"net": "/W1_A", "x": 109.0, "y": 18.2}]}
```
Net names EXACTLY as in netlist.net (most carry a leading `/`, e.g.
`/W1_A`; power rails are `+24V`, `GND`, `+5V`, `+3V3`; switching nodes are
`Net-(U1-SW)` … `Net-(U7-SW)`). Each `pts` polyline becomes chained
segments. Vias are 0.5/0.3 (JLC minimum, already net-classed).

## Netclass widths (assigned in .kicad_pro — DRC enforces)

- `+24V`, `Net-(Ux-SW)`: **0.5 mm** (Power_24V)
- `_A` string-anode nets (`/W1_A`…`/W4_A`, `/R_A`, `/B_A`, `/DR_A`): **1.0 mm**
- `_K` string-cathode nets: **0.8 mm**
- everything else (CTRL, PWM, chains, +5V, +3V3): Default **0.25 mm** usable
  (chains carry DC string current — use **0.3–0.5 mm** where they're long)

## Placement map (absolute mm)

Input/logic cluster (x 0–100): J1(8,6) DC-in TB · F1(12,15) fuse clips ·
J7(32,6) switch TB · C2(43,13) 220µF · C1(52,15,rot90) · U8(48,5,rot90) IRM
hdr · U9(58.5,15) SOT-223 · C3(66,15.5,rot90) · C4(70,15.5,rot90) ·
J6(78,5,rot90) ESP32 hdr · R1–R4(88/91.5/95/98.5, y12, rot90) ·
R5–R8(same x, y17.5, rot90) · MH1(20,4) NPTH.
Headers (1×6 2.54, rot 270, **pin 1 at Hx facing right**, pins descend x by
2.54, pads 1.7 mm dia at y 4.65..6.35): **J2 Hx=109 · J3 233 · J4 369 ·
J5 475**. Mounting holes NPTH 3.2: MH2(190,10) MH3(390,10) MH4(560,10).
Channel cells (x0 per driver): **U1 x0=121 · U5 155 · U6 196 · U2 245 ·
U3 330 · U7 398 · U4 438**.

## Channel-cell geometry (x0-relative; verified from .pretty files)

| element | position (x0+, y) | pad extents (x0-relative) | nets |
|---|---|---|---|
| L pad1 | 12.95, 10 | x 11.5–14.4, y 7.3–12.7 (pad 2.9×5.4) | `Net-(Ux-SW)` |
| L pad2 | 3.05, 10 | x 1.6–4.5, y 7.3–12.7 | `_K` of that channel |
| D cathode | 18.6, 2.5 | x 17.7–19.5, y 1.25–3.75 | `+24V` |
| D anode | 18.6, 6.5 | x 17.7–19.5, y 5.25–7.75 | `Net-(Ux-SW)` |
| U pin1 SW | 17.36, 9.05 | x 16.7–18.03, y 8.75–9.35 | `Net-(Ux-SW)` |
| U pin2 GND | 17.36, 10.0 | y 9.7–10.3 | GND (zones agent) |
| U pin3 CTRL | 17.36, 10.95 | y 10.65–11.25 | `/CTRL_*` |
| U pin4 SET | 19.64, 10.95 | x 18.97–20.3, y 10.65–11.25 | `_A` |
| U pin5 VIN | 19.64, 9.05 | x 18.97–20.3, y 8.75–9.35 | `+24V` |
| C100n pin2 | 21.42, 9.05 | x 20.97–21.87, y 8.575–9.525 | `+24V` |
| C100n pin1 | 22.97, 9.05 | x 22.52–23.42 | GND |
| C22µ pin2 | 24.575, 9.05 | x 24.0–25.15, y 7.7–10.4 (1210) | `+24V` |
| C22µ pin1 | 27.525, 9.05 | x 26.95–28.1 | GND |
| RSET pin1 | 18.54, 16 | x 17.93–19.15, y 14.32–17.68 (2512) | `_A` |
| RSET pin2 | 24.46, 16 | x 23.85–25.08 | `+24V` |

Free horizontal corridors through a cell: y ≈ 3.9–5.1 (between the two D
pads), y ≈ 8.0–8.4 (above U pads / below D anode), y ≈ 12.85–14.17 (between
L pads' top 12.7 and RSET top 14.32 — fits ONE 1.0 mm track at y≈13.65),
y ≈ 17.8–19.7 (below RSET pads). Blocked x-lanes per cell: whatever YOU and
other groups place — the DRC oracle is the referee.

## Net → endpoint table (absolute positions via pad_pos)

White channels (local pairs): W1: U1↔J2 pin1(109) A / pin2(106.46) K ·
W2: U2↔J3 pin1(233) / pin2(230.46) · W3: U3↔J4 pin1(369) / pin2(366.46)
(**header RIGHT of cell**) · W4: U4↔J5 pin1(475) / pin2(472.46) (right).
Colour channels (anode at J2/J4, cathode returns far right):
- `/R_A`: J2 pin3 (103.92, 5.5) + U5 pin4 + R14 pin1 (x0=155)
- `/B_A`: J2 pin5 (98.84, 5.5) + U6 pin4 + R15 pin1 (x0=196)
- `/DR_A`: J4 pin5 (**358.84**, 5.5) + U7 pin4 + R16 pin1 (x0=398)
  (header pin n x = Hx − (n−1)×2.54; the 364.62 previously listed here was wrong)
- `/R_K`: J5 pin4 (467.38, 5.5) + L5 pin2 — **309 mm run through cells U6,U2,U3,U7,U4**
- `/B_K`: J3 pin6 (220.3, 5.5) + L6 pin2
- `/DR_K`: J5 pin6 (462.3, 5.5) + L7 pin2
Inter-header chains (driver PCB completes the colour-series joins):
`/R_J23` J2.4(101.38)→J3.3(227.92) · `/R_J34` J3.4(225.38)→J4.3(363.92) ·
`/R_J45` J4.4(361.38)→J5.3(469.92) · `/B_J23` J2.6(96.3)→J3.5(222.84) ·
`/DR_J45` J4.6(356.3)→J5.5(464.84)
CTRL (B.Cu corridor planned): `/CTRL_W` = R1.1(88,12.82) + R5.2(88,16.68) +
U1.3, U2.3, U3.3, U4.3 · `/CTRL_R` R2.1(91.5) + R6.2 + U5.3 · `/CTRL_B` R3.1
(95) + R7.2 + U6.3 · `/CTRL_DR` R4.1(98.5) + R8.2 + U7.3.
PWM: J6.1–4 (78 / 80.54 / 83.08 / 85.62, y 5) → R1–R4 pin2 (88 / 91.5 / 95 /
98.5, y 11.18). Input: `/VIN_RAW` J1.1(8,6)→F1.1(12,15) · `/SW_A`
F1.2(26.7,15)→J7.1(32,6) · `+24V` originates J7.2(37,6) → C2.1(43,13),
C1.2(52,14.22), U8.1(48,5) + every cell's VIN cluster · `+5V` U8.3(53.08,5),
C3.2(66,14.55), U9.3(55.35,17.3) · `+3V3` U9.2(55.35,15), C4.2(70,14.55),
J6.6(90.7,5). GND is handled by the zones agent (B.Cu pour + vias).

## Working band plan (strong hints — the DRC oracle arbitrates)

- **F.Cu +24V trunk, 1.0 mm wide at y = 2.2** from x≈37 to x≈575. KEY FACT:
  every D cathode pad (y 1.25–3.75) is CROSSED by the trunk at y 1.7–2.7 —
  same net ⇒ direct connection, no drop needed for the diodes.
- Per-cell +24V cap feeds (g1's FINAL routed geometry — these segments exist
  on disk and are immutable): ONE 0.5 mm vertical at **x0+21.0** from trunk
  down to y=16 (passes through C100n pin2), a 0.5 mm branch at y 9.05 to
  U pin5, a shelf at y 11.0 to C22µ pin2, and a y=16 horizontal to RSET
  pin2. The originally-planned **x0+29 drops were abandoned** (they shorted
  header pads at three cells) — the B.Cu corridor y 16.8–19.5 is therefore
  FREE of +24V crossings (nearest +24V copper is the y 16.0–16.25 shelf).
  The +24V trunk ends at x=459.5 (last drop), not x≈575.
- SW loops (keep SHORT — high dI/dt): D anode → y 8.0 → U pin1; L pad1 →
  horizontal y 9.05 → U pin1. All F.Cu.
- `_A` band: **y = 13.65** (1.0 mm) — W1/W2 left-going, W3/W4 right-going.
- `_K` band left-going local (W1/W2): **y = 7.0**; right-going (W3/W4):
  **y = 4.2** (0.8/0.5 mm, between the D pads' y windows).
- **B.Cu corridor y ≈ 16.8–19.5** (below the GND-pour zone which will cover
  y 1–16.5): chains (0.3–0.5), CTRL (0.25), and the long colour nets
  (`/R_K` 0.8, `/R_A` `/B_A` `/DR_A` 1.0, `/B_K` `/DR_K` 0.8) with vias at
  both ends. Lanes can be REUSED by different nets in disjoint x-ranges.
- KNOWN conflicts (updated for g1's final geometry): the x0+21.0 +24V
  verticals cross the y=13.65 _A band at x 142/176/217/266/351/419/459 —
  REAL conflicts only at U3 x=351 (W3_A spans 349.64–369) and U4 x=459
  (W4_A spans 457.64–475); W3_K/W4_K y=4.2 runs cross the x=351/x=459
  verticals; chain verticals at J4 (361.38, 356.3) cross W3's bands.

## Ground rules

1. NEVER edit `gen_pcb.py` placement, footprints, or existing emitters.
   Your only output channel is `ROUTES_EXTRA.json` in YOUR scratch copy.
2. Work in your scratch copy: `cp -r "C:/Users/Akshat Jagdev/Desktop/aquarium_v0/hardware/kicad_project" "<your scratch dir>"` (quote paths —
   spaces!). NEVER touch the real project directory.
3. Iterate: write overlay → `python gen_pcb.py` → DRC → read drc.json → fix.
   Exit gate: **0 violations** AND zero unconnected items naming your nets.
4. Same-net overlaps are connections; abuse that to land tracks ON pads.
5. Avoid vias inside pad copper (assembly). ≥0.15 mm from foreign copper,
   0.3 mm from board edge, keep 1 mm from MH holes (NPTH clearance).
6. Return your FINAL tested overlay verbatim in the structured output.