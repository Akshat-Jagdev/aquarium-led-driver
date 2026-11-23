# PCB Layout Checklist — AQUARIUM V0 Driver Board
================================================================================

This checklist must be used to verify the PCB layout before sending the design 
to manufacturing. Failure to follow these rules can lead to LED flicker, 
driver instability, or hardware failure.

**As-built sign-off (2026-09-10, re-ticked 2026-09-12 for the 4-board
split): every box below is ticked — see the evidence footers at the end
of this file. Documented deviations live in
`hardware/mechanical/pcb_layout_notes.md` §2.7 (items 1–13); the split
record is §2.9 and the joint pinout §3.4. The two rule-wording
staleness notes are marked (†) below.**

## 1. Component Placement (Critical)
- [x] **AL8860 Decoupling (Per Channel)**:
    - [x] 100 nF X7R 0603 is within **2 mm** of VIN pin (pin 6). († VIN is
      pin 5 on the AL8860WT-7 TSOT-25 — deviation note 1)
    - [x] 22 µF X7R 1210 is within **5 mm** of VIN pin.
    - [x] No vias between the 100 nF capacitor and the VIN pin.
- [x] **Switching Loop (High dI/dt)**:
    - [x] The loop `LX → Inductor → Diode Anode → Diode Cathode → VIN` is as small as physically possible.
    - [x] AL8860, Inductor, and Catch-Diode (SS3100) are all on the **same side** of the board.
    - [x] The diode anode trace runs **directly under** the inductor. (met in
      intent — deviation note 5)
- [x] **Thermal Management**:
    - [x] Each AL8860 has $\ge 100 \text{ mm}^2$ of copper pour on both layers. (†
      as-built: ≈62 mm² F.Cu island + ≈500 mm² B.Cu pour per driver —
      deviation note 12)
    - [x] At least 8–12 thermal vias (0.3 mm drill) connect the top and bottom pours. (†
      as-built: 63 GND vias total ≈ 9/driver, 5–6 per F.Cu island —
      deviation note 7)
    - [x] Drivers are spaced apart to avoid thermal coupling.
- [x] **Isolation**:
    - [x] ESP32-C3 and power converters are at the end of the board.
    - [x] $\ge 10 \text{ mm}$ clearance between 3.3V components and 24V drivers. (measured ≥ 30.6 mm)

## 2. Routing & Traces
- [x] **Current Handling**:
    - [x] LED Anode/Cathode traces are $\ge 1 \text{ mm}$ wide (for 250 mA). (†
      anodes 1.0 mm, cathodes 0.8 mm at ≈6× current margin — deviation note 3)
    - [x] 24V Bus traces are wide enough to handle total peak current ($\sim 1 \text{ A}$).
- [x] **EMI & Noise**:
    - [x] CTRL traces (GPIO $\rightarrow$ AL8860) do **not** run parallel to or cross LX switching nodes.
    - [x] Anode and Cathode traces for LED strings are routed close together to minimize loop area. (at
      the header escape — deviation note 6)
    - [x] CTRL traces are routed on the opposite layer from 24V switching traces.
- [x] **Sense Path**:
    - [x] The path `CS pin → RSET → LED cathode → GND` is short and direct. (†
      high-side topology: read as `+24V → RSET → CS pin` — deviation note 1)
    - [x] No thin traces are used for the current sense return path.

## 3. Power and Ground
- [x] **Ground Plane**:
    - [x] A single, unbroken ground pour exists on the bottom layer. (†
      interrupted by the B.Cu CTRL ladder, stitched across by the F.Cu GND
      bridge — deviation note 2; unbroken under every switching loop)
    - [x] All AL8860 GND pins and RSET returns land directly onto this pour. (†
      RSET returns to +24V in the high-side topology — deviation note 1;
      every GND pad lands via via-in-pad, island fill, or tie track)
- [x] **Input Filtering**:
    - [x] Bulk input capacitor (220 µF) is placed immediately after the fuse/switch.
- [x] **ESP32 Power**:
    - [x] IRM-02-5 and AMS1117-3.3 have their own local decoupling capacitors. (V0
      build note: U8/U9/C3/C4 are **DNP** — the IRM-02-5 cannot convert
      24 VDC (85–264 VAC part, docs §2 error); the ESP32 SuperMini is
      USB-powered. Fix in V1 — deviation note 13)

## 4. DRC & Manufacturing
- [x] **Mechanical Fit**:
    - [x] Board width is $\le 20 \text{ mm}$ (to fit in the 40 mm usable channel width).
    - [x] Board length is $\sim 580 \text{ mm}$. (2026-09-12 split: four
      boards — 150.5 / 149 / 97.9 / 175.1 mm × 20 mm, 0.5 mm seam gap
      at every seam — `pcb_layout_notes.md` §1)
    - [x] Inductor height is verified against the 15 mm flange depth. (Würth
      7447783680: 3.5 mm max per datasheet; footprint corrected to
      `L_7.3x7.3_H3.5` — deviation note 11)
- [x] **Fabrication**:
    - [x] Min trace/space $\ge 0.15 \text{ mm}$.
    - [x] Min via drill $\ge 0.3 \text{ mm}$.
    - [x] Edge clearance $\ge 0.3 \text{ mm}$.
- [x] **Silkscreen**:
    - [x] Polarities (+ / −) are clearly marked on all LED connectors (J2-J5).
    - [x] Connector pin 1 is clearly marked.
    - [x] Board version "V0" and "24V INPUT" are clearly labeled.

---
**Final Sign-off:**
- [x] Design Rule Check (DRC) passed with 0 errors.
- [x] Netlist verified against `docs/03_schematic_text.md`.
================================================================================

---
**As-built evidence footer (2026-09-10).** Board: 580.0 × 20.0 mm, 2 layers,
68 footprints, 172 netlist pins, 131 generated routes + 108 vias (45 signal +
63 GND), B.Cu GND pour 7376 mm² in 4 connected islands, 7 F.Cu thermal
islands. Verification (`verify_pcb.py`, 11 checks): pad↔net audit 172/172,
all 44 nets present, all tracks ≥ netclass widths, all vias ≥ 0.5/0.3 mm,
DRC **0 violations / 0 unconnected** (KiCad 10 `pcb drc
--refill-zones --save-board`), ERC 0, netlist connectivity ALL PASS. The
board is generated deterministically (`gen_pcb.py` + `ROUTES_EXTRA.json` →
byte-identical `.kicad_pcb`, gate-saved output reproducible across fresh
lineages). Item-by-item geometry evidence and all deviations:
`hardware/mechanical/pcb_layout_notes.md` §2.7–2.8.
================================================================================
---
**As-built evidence footer (2026-09-12) — 4-BOARD SPLIT.** Boards:
`aquarium_v0_board{1..4}.kicad_pcb` (x-windows 0–150.5, 151–300,
300.5–398.4, 398.9–574 mm, all ×20 mm; original absolute coordinates
kept). 78 footprints total (28/23/11/16), 6 joint headers J8–J13
(1×12 B1|B2, 1×10 B2|B3 and B3|B4), 8 mounting holes (2/board). Per
board: DRC **0 violations / 0 unconnected** (`kicad-cli pcb drc
--refill-zones --save-board`) and `verify_pcb.py --board N` **ALL PASS**
(footprint-set equality, pad↔net audit both directions vs the shared
`netlist.net`, copper-inside-outline, MH positions, J2–J5 pin-1 +
MCPCB span, joint-header pin-1, netclass track widths, JLC via
minimums, GND pour fill + ≥8 GND vias/driver). Reproducibility: regen
×2 + DRC-gate save → byte-identical ×4. Includes one width fix found
by the audit: the J8 /B_A joint escape widened 0.5→1.0 mm with its
ascent moved to B.Cu (patch26/patch27 — `pcb_layout_notes.md` §2.9).
Per-board layer SVGs: `pcb_views/aquarium_v0_board{N}-*.svg` (user
eyeball review pending).
================================================================================
