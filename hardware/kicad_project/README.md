# KiCad Project — V0 Aquarium Light

> Scaffold for the V0 schematic capture and PCB layout.
> Create the `.kicad_pro` and `.kicad_sch` in KiCad 8 and save them here.

## 1. How to create the project

1. Open **KiCad 8** (project editor).
2. **File → New Project** → name it `aquarium_v0` → save into this folder.
3. KiCad creates:
   - `aquarium_v0.kicad_pro` — project settings
   - `aquarium_v0.kicad_sch` — top-level schematic (initially empty)
4. Use **Schematic Editor → File → Add Sheet** to break the schematic into
   sections (recommended for readability):
   - `01_power.kicad_sch` — input, fuse, switch, 24 V bus, ESP32 power tree
   - `02_white_drivers.kicad_sch` — 4× AL8860 white channels
   - `03_colour_drivers.kicad_sch` — red + blue + deep-red AL8860 channels
   - `04_esp32_interface.kicad_sch` — ESP32 header + GPIO buffer network

## 2. Library plan

| Part | Source |
|------|--------|
| AL8860W6-7 (SOT23-6) | Diodes Inc KiCad library, or generic SOT-23-6 symbol with custom footprint |
| Würth 7447783680 (WE-PD series) | Würth WE-PD library, or KiCad "Inductor_SMD" + manual WE-PD footprint |
| Vishay WSL2512 | KiCad `Resistor_SMD:R_2512_6332Metric` |
| SS3100 (SMA) | KiCad `Diode_SMD:D_SMA` |
| ESP32-C3 SuperMini | Custom symbol + custom footprint (no KiCad library entry) |
| LUXEON 5050, 2835, Rubix | Custom symbols + footprints (see below) |
| 220 µF Nichicon UPW radial | KiCap `CP_Radial_D10.0mm_P5.00mm` or similar |
| Mean Well LRS-35-24 | Mechanical only — represented as off-board connector |
| IRM-02-5 | Off-board DIP module — represented as 4-pin connector |

## 3. Custom symbol / footprint list

You'll need to draw these by hand using KiCad's Symbol Editor and
Footprint Editor:

1. **ESP32-C3 SuperMini module**
   - Symbol: 1×6 header with `5V, GPIO0, GPIO1, GND, 3V3, ...` pins
   - Footprint: 2× 1×12 pin header strip, 2.54 mm pitch, board-edge
     mounting
2. **LUXEON 5050 HE Plus**
   - Symbol: LED with anode / cathode / thermal pad
   - Footprint: 5050 SMD with thermal pad
3. **LUXEON 2835 (Red and SunPlus)**
   - Symbol: LED with anode / cathode / thermal pad
   - Footprint: 2835 SMD
4. **LUXEON Rubix (L1RX-RYL1000000000)**
   - Symbol: LED with 2 anode + 2 cathode + thermal pad
   - Footprint: Rubix-style SMD with thermal pad

## 4. Net classes

Define these in **Project → Design Rules → Net Classes**:

| Net class | Clearance | Track width | Via drill | Use |
|-----------|-----------|-------------|-----------|-----|
| Default | 0.15 mm | 0.20 mm | 0.3 mm | Signals, CTRL, 3V3 |
| Power_24V | 0.30 mm | 0.50 mm | 0.5 mm | 24 V bus |
| LED_Anode | 0.30 mm | 1.00 mm | 0.5 mm | LED anode traces (250 mA) |
| LED_Cathode | 0.30 mm | 0.80 mm | 0.5 mm | LED cathode / RSET |

## 5. Layout checklist (before generating Gerbers)

- [ ] Board outline: ~580 × ≤14 mm slender strip (extrusion cavity) — see
      `../mechanical/pcb_layout_notes.md` §1
- [ ] MCPCB headers J2–J5: 6-pin each, pinout per `pcb_layout_notes.md` §3.2
      (colour series chains completed with PCB traces between headers)
- [ ] All decoupling caps within 2 mm of their IC pin (AL8860 × 7)
- [ ] Switching loop (LX, L, D1) area < 50 mm² per channel
- [ ] 100 mm² thermal copper under each AL8860, stitched with vias
- [ ] ESP32 section separated from 24 V section by ≥ 10 mm
- [ ] All MCPCB connectors labelled + and −
- [ ] Fuse clearly marked F1 with value
- [ ] Mounting holes dimensioned and clear of copper
- [ ] DRC clean, no warnings

## 6. Fabrication output

Export Gerbers + drill files into `hardware/kicad_project/gerbers/` and
zip them before uploading to JLCPCB / PCBWay. Use these settings:

- Layers: top, bottom, silkscreen top, soldermask top + bottom
- 1.6 mm board thickness
- 1 oz copper
- HASL-lead-free finish (cheapest) or ENIG (better for hand soldering)
- 4× M3 mounting holes plated (or non-plated — cheaper, fine for our use)

## 7. Open items

- Final ESP32-C3 SuperMini symbol/footprint geometry — measure from the
  physical board before drawing
- Confirm Mean Well IRM-02-5 pinout from datasheet before symbolising
- Decide whether to use 2 oz copper for the LED anode traces (cleaner
  at high current, +₹30 per board)
