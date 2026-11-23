# Aquarium LED Driver Panel (V0)

Open-source hardware project: a scientifically engineered aquarium LED light for fish-colour enhancement, designed for low-cost manufacture in India.

**What this repo contains — the complete engineering package:**
- **Hardware**: KiCad 8 sources for a 4-board panel (2 MCPCB LED-board designs × 2 + driver board), dual-rail +24 V/+12 V, DRC-clean layouts with scripted netlist verification
- **Firmware**: ESP32-C3 Arduino sketches — 4 light profiles, 2 kHz / 12-bit PWM, per-channel dimming
- **Engineering tools** (Python): power/thermal calculator, PWM frequency analyser, LED lifetime estimator, BOM cost calculator
- **Test procedures**: TP-01 → TP-07 (bench bring-up, optical comparison, 2-hr thermal soak, spectrum, 100-hr reliability)
- **Documentation**: design-decision rationale, driver-architecture audit (AL8860 buck topology), risk register, schematic
- **Business analysis**: unit economics, volume cost projections, competitive landscape, go-to-market

> **Stage**: V0 prototype — all 4 PCBs routed and verified, panel fabricated and received (Oct 2026); bench bring-up in progress.
> **Target retail**: ₹3,000–4,000 · **Production BOM (incl. LEDs)**: ~₹2,542 @ qty 500, ~₹2,340 @ qty 1000 · **Target**: ≤₹2,000 @ qty 5000+

---

## 1. Project Structure

```
aquarium_v0/
├── README.md                      ← this file (master index)
│
├── docs/
│   ├── 00_project_brief.md        ← full business + product specification
│   ├── 01_design_decisions.md     ← all design choices and their rationale
│   ├── 02_audit_report.md         ← full audit of original AL8860 architecture
│   ├── 03_schematic_text.md       ← text-form schematic of V0
│   └── 04_risk_register.md        ← known risks and how to mitigate them
│
├── hardware/
│   ├── kicad_project/             ← KiCad 8 sources (schematic + 4-board PCB layout)
│   ├── mechanical/
│   │   ├── extrusion_dims.md      ← aluminium extrusion specifications
│   │   ├── pcb_layout_notes.md    ← critical PCB layout rules
│   │   └── assembly_drawing.md    ← mechanical assembly
│
├── firmware/
│   ├── pwm_test_sketch.ino        ← ESP32-C3 PWM control (4 profiles, 2 kHz)
│   ├── esp32_pin_map.md           ← ESP32-C3 pin assignment
│   └── build_instructions.md      ← how to compile and upload
│
├── bom/
│   ├── BOM_v0_prototype.csv       ← bill of materials, 1-unit pricing
│   ├── BOM_v0_production_500.csv  ← bill of materials, 500-unit pricing
│   ├── PARTS_LIST.md              ← complete parts list with verified links (all sources)
│   ├── india_suppliers.md         ← contact list for Indian distributors
│   ├── lcsc_links.md              ← direct LCSC links for every part
│   └── digikey_mouser_links.md    ← backup sourcing for parts not on LCSC
│
├── datasheets/
│   ├── AL8860_diodes.pdf          ← driver IC
│   ├── LUXEON_5050_HE_Plus.pdf    ← white LED
│   ├── LUXEON_2835_Red.pdf        ← 625 nm LED
│   ├── LUXEON_Rubix_448.pdf       ← blue LED
│   ├── LUXEON_SunPlus_660.pdf     ← deep-red LED
│   ├── LRS-35-24_meanwell.pdf     ← PSU
│   ├── WSL2512_vishay.pdf         ← current-sense resistors
│   ├── 7447783680_wurth.pdf       ← inductor
│   └── SS3100_diodes.pdf          ← schottky diode
│
├── test_procedures/
│   ├── TP-01_one_channel_bench.md ← validate ONE AL8860 on perfboard
│   ├── TP-02_full_pcb_bench.md    ← validate full V0 PCB
│   ├── TP-03_optical_compare.md   ← compare profiles A/B/C/D visually
│   ├── TP-04_thermal_2hr.md       ← 2-hour thermal soak test
│   ├── TP-05_spectrum_test.md     ← spectrometer measurement (when you have one)
│   ├── TP-06_fish_appearance.md   ← qualitative test with ornamental fish
│   └── TP-07_reliability_soak.md  ← extended run (target 100 hr)
│
├── business/
│   ├── competitive_landscape.md   ← TICA vs Chihiros vs others
│   ├── unit_economics.md          ← per-unit cost and margin model
│   ├── volume_projection.md       ← 1 / 100 / 500 / 1000 unit cost
│   └── go_to_market.md            ← retail / e-commerce / aquarium shops
│
└── tools/
    ├── power_thermal_calculator.py
    ├── bom_cost_calculator.py
    ├── pwm_freq_analyzer.py
    └── led_lifetime_estimator.py
```

---

## 2. Quick Start (Layman)

If you are new to this project and want to start building today:

1. **Read** `docs/00_project_brief.md` (15 min) — full picture
2. **Read** `docs/02_audit_report.md` (20 min) — what to build and WHY
3. **Read** `docs/03_schematic_text.md` (15 min) — exact wiring
4. **Open** `bom/BOM_v0_prototype.csv` (5 min) — list of parts to order
5. **Order parts** from `bom/PARTS_LIST.md` (complete parts list with verified links for every component, including LEDs) and `bom/lcsc_links.md` and `bom/india_suppliers.md`
6. **Follow** `test_procedures/TP-01_one_channel_bench.md` — build ONE channel first
7. **Run** `tools/power_thermal_calculator.py` — verify numbers any time
8. **When ONE channel works** → move to full KiCad PCB design

---

## 3. Critical Numbers (cheat sheet)

| Item | Value |
|------|-------|
| Input voltage | 24 V DC |
| Total power (all channels max) | ~22 W |
| PSU current (full load) | ~0.92 A |
| White current per string | 250 mA |
| Red current | 120 mA |
| Blue current | 303 mA (start conservative) |
| Deep red current | 120 mA |
| PWM frequency | 2 kHz (NOT 400 Hz) |
| PWM resolution | 12-bit |
| AL8860 count | 7 (4 white, 1 red, 1 blue, 1 deep red) |
| RSET (white / red / blue / DR) | 0.40 / 0.82 / 0.33 / 0.82 Ω |
| Inductor | 68 µH shielded, ≥0.95 A Isat |
| Schottky | 100 V / 3 A (SS3100) — NOT SS24 |
| Input cap | 22 µF / 50 V X7R 1210 (NOT 10 µF 0805) |
| LED TC limit | 85 °C |
| Fuse | 2 A slow-blow |
| Controller | ESP32-C3 SuperMini, direct GPIO → 1 kΩ → CTRL |
| (NO 2N7002) | — |

---

## 4. What you already own (or have ordered)

- 12× White LED: Luminus MP5050-240P (5700K)
- 4× Red LED: LUXEON 2835 Red 625 nm
- 2× Royal Blue LED: Cree XPGDRY-LS-0000-00501
- 2× Deep Red LED: LUXEON SunPlus 660 nm
- 1× Mean Well LRS-35-24
- 1× ESP32-C3 SuperMini

---

## 5. What you still need to order

See `bom/BOM_v0_prototype.csv` and `bom/lcsc_links.md`. Total estimate: **₹3,500–4,000** for the prototype (1 unit) including passive components, PCB, and mechanical parts.

---

## 6. Current status

- [x] Architecture defined
- [x] LEDs selected and ordered
- [x] PSU selected and ordered
- [x] Controller selected and ordered
- [x] Driver IC selected
- [x] Audit of driver architecture complete
- [x] Schematic text written
- [x] BOM with India sourcing prepared
- [x] BOM production-500 ready
- [x] PWM firmware written
- [x] Python calculators written (all 4 tools verified to run)
- [x] Test procedures drafted (TP-01 → TP-07)
- [x] Hardware mechanical documentation drafted (extrusion, PCB layout, assembly)
- [x] ESP32 pin map + build instructions
- [x] KiCad project scaffold documented
- [x] Business documents drafted (competitive landscape, unit economics, volume projection, go-to-market)
- [x] Risk register drafted
- [x] Design-decision rationale written
- [x] KiCad schematic capture (aquarium_v0.kicad_sch, Sep 14 netlist is truth)
- [x] 4-board PCB layout routed (gen_pcb.py + ROUTES_EXTRA.json; DRC clean on all boards, verify_netlist.py passes)
- [x] MCPCB + driver PCB Gerbers — panel fabricated and received (Oct 2026); see `hardware/assembly/`
- [ ] One-channel bench prototype (Phase B)
- [ ] Full PCB prototype (Phase C)
- [ ] Optical test against TICA (TP-03)
- [ ] Thermal verification (TP-04)
- [ ] Spectrum measurement (TP-05)
- [ ] Reliability soak (TP-07)
- [ ] Production design (V1)

---

## 7. Design decisions (resolved)

Before PCB layout, decide:
- Length: 60 cm or 90 cm? (DECIDED: 60 cm)
- Diffuser: clear, opal, or both? (DECIDED: opal)
- MCPCB: **DECIDED** — 4 small boards, 2 designs × 2 (5-LED, 140 × 20 mm; see `extrusion_dims.md` §3)
- Mounting: hanging kit, rim-mount bracket, or both? (DECIDED: rim-mount bracket)
