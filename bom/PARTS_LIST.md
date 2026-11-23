# Complete Parts List — Aquarium V0 / COLORBOOST

> Every component required to build ONE V0 prototype (qty 1).
> Includes: LEDs (already owned), drivers, passives, power, mechanical.
> All parts include ≥ 1 verified sourcing link.

> **Order strategy**
> - Order ICs, passives, RSETs from **LCSC** (cheapest, 7-15 day shipping to India)
> - Order Mean Well LRS-35-24 and IRM-02-5 from **Mouser India / Sunrom / Evelta**
> - Order ESP32-C3 SuperMini from **Robu.in** (fast Indian delivery)
> - Order aluminium extrusion, acrylic diffuser, mounting brackets from **local suppliers**
> - Order Mean Well PSU specifically from **Probots.co.in** (Indian stock)

---

## 1. LEDs (already owned — for reference)

| # | Part | MPN | Qty | Channel | Buy link |
|---|------|-----|-----|---------|----------|
| 1.1 | LUXEON 5050 HE Plus 5700K | Luminus MP5050-240P | 12 | White (4 strings × 3) | [Luminus Product Page](https://www.luminus.com/products/standardmidpower) | [Luminus Datasheet](https://download.luminus.com/datasheets/Luminus_MP5050_240P_Datasheet.pdf) |
| 1.2 | LUXEON 2835 Color Red 625 nm | L128-RED10035000002835 | 4 | Red (1 string × 4) | [Mouser India](https://www.mouser.in/ProductDetail/Lumileds/L128-RED10035000002835) · [Lumileds product page](https://lumileds.com/products/color-leds/luxeon-2835-color-line/) |
| 1.3 | Cree Royal Blue 451 nm | XPGDRY-LS-0000-00501 | 2 | Blue (1 string × 2) | [ICMiles](https://www.icmiles.com/devices/detail/creeled/xpgdryls000000501-10524810) | [Cree Datasheet](https://downloads.cree-led.com/files/ds/x/XLamp-XE-B.pdf) |
| 1.4 | LUXEON SunPlus 2835 Deep Red 660 nm | L1SP-DRD0002800000 | 2 | Deep red (1 string × 2) | [Lumileds product page](https://lumileds.com/products/horticulture-leds/sunplus-series/) |

> **CRITICAL FOOTPRINT NOTE**: The Royal Blue LED (XPGDRY) is a **3535 package**. All other LEDs in the design are **5050/2835**. If designing the PCB, the Blue channel pads must be updated to 3.5mm x 3.5mm.

> All four LED datasheets are also copied to `datasheets/` (LUXEON_5050_HE_Plus.pdf, LUXEON_2835_Red.pdf, LUXEON_Rubix_448.pdf, LUXEON_SunPlus_660.pdf).

---

## 2. Driver ICs

| # | Part | MPN | Qty | Buy link (LCSC) | Buy link (backup) |
|---|------|-----|-----|------------------|--------------------|
| 2.1 | 40 V 1.5 A Buck LED Driver, SOT23-6 | AL8860W6-7 | 7 (+3 spares) | [LCSC C460356](https://www.lcsc.com/product-detail/C460356.html) | [DigiKey IN](https://www.digikey.in/en/products/detail/diodes-incorporated/AL8860W6-7/5637410) · [Mouser IN](https://www.mouser.in/ProductDetail/Diodes-Inc/AL8860W6-7) |
| 2.2 | 100 V 3 A Schottky, SMA | SS3100-E3/8 | 7 (+3 spares) | [LCSC C2480](https://www.lcsc.com/product-detail/C2480.html) | [DigiKey IN](https://www.digikey.in/en/products/detail/diodes-incorporated/SS3100-E3/8) · [Mouser IN](https://www.mouser.in/ProductDetail/Vishay/SS3100-E3) |

> **CRITICAL**: Do NOT use SS24 (40 V rating). 24 V input + 17.55 V white string Vf = 41.55 V reverse voltage on the catch diode. SS24 will avalanche.

---

## 3. Passives — magnetics

| # | Part | MPN | Qty | Buy link (LCSC) | Buy link (backup) |
|---|------|-----|-----|------------------|--------------------|
| 3.1 | 68 µH 0.95 A shielded power inductor | Würth 7447783680 (WE-PD) | 7 (+3 spares) | [LCSC C184706](https://www.lcsc.com/product-detail/C184706.html) | [Mouser IN](https://www.mouser.in/ProductDetail/Wurth-Elektronik/7447783680) · [Element14 IN](https://in.element14.com/wurth-elektronik/7447783680) |

---

## 4. Passives — capacitors

| # | Part | MPN | Qty | Buy link (LCSC) | Buy link (backup) |
|---|------|-----|-----|------------------|--------------------|
| 4.1 | 22 µF / 50 V X7R ceramic, 1210 (7× input bypass + 1× C12V on +12V rail — 22 µF supersedes the schematic's 10 µF, same 1210 case, better DC-bias margin) | Murata GRM32ER71H226KE15L | 8 (+3 spares) | [LCSC C13753](https://www.lcsc.com/product-detail/C13753.html) | [DigiKey IN](https://www.digikey.in/en/products/detail/murata-electronics/GRM32ER71H226KE15L) · [Mouser IN](https://www.mouser.in/ProductDetail/Murata/GRM32ER71H226KE15L) |
| 4.2 | 100 nF / 50 V X7R ceramic, 0603 | Samsung CL10B104KB8NFNC | 20 | [LCSC C346191](https://www.lcsc.com/product-detail/C346191.html) | (any brand OK) |
| 4.3 | 1 µF / 50 V X7R ceramic, 0805 | Samsung CL21B105KBFNNNE | 10 | [LCSC C28323](https://www.lcsc.com/product-detail/C28323.html) | (any brand OK) |
| 4.4 | 220 µF / 50 V electrolytic, radial | Nichicon UPW1H221MPD | 1 (+1 spare) | (not on LCSC) | [Element14 IN](https://in.element14.com/nichicon/upw1h221mpd) · [Mouser IN](https://www.mouser.in/ProductDetail/Nichicon/UPW1H221MPD) |

> **CRITICAL**: Do NOT use 10 µF 0805 for the 22 µF position. DC-bias derating makes it ~4 µF at 24 V. The 1210 case with 50 V rating measures ~18-20 µF at 24 V.

---

## 5. Passives — current sense resistors (Vishay WSL2512)

| # | Part | MPN | Qty | Channel | Buy link (LCSC) | Buy link (backup) |
|---|------|-----|-----|---------|------------------|--------------------|
| 5.1 | 0.40 Ω 1 % 1 W 2512 | Vishay WSL2512R4000FEA | 4 (+1 spare) | White (250 mA) | [LCSC C2990117](https://www.lcsc.com/product-detail/C2990117.html) | [DigiKey IN](https://www.digikey.in/en/products/detail/vishay-dale/WSL2512R4000FEA) |
| 5.2 | 0.82 Ω 1 % 1 W 2512 | Vishay WSL2512R8200FEA | 2 (+1 spare) | Red + Deep-red (120 mA) | [LCSC C2990150](https://www.lcsc.com/product-detail/C2990150.html) | [DigiKey IN](https://www.digikey.in/en/products/detail/vishay-dale/WSL2512R8200FEA) |
| 5.3 | 0.33 Ω 1 % 1 W 2512 | Vishay WSL2512R3300FEA | 1 (+1 spare) | Blue (303 mA) | [LCSC C2990101](https://www.lcsc.com/product-detail/C2990101.html) | [DigiKey IN](https://www.digikey.in/en/products/detail/vishay-dale/WSL2512R3300FEA) |

> Use 1 % tolerance only. 5 % tolerance gives ±12 % current error → uneven brightness and uneven ageing.

---

## 6. Passives — standard 0603 resistors

| # | Part | MPN | Qty | Purpose | Buy link (LCSC) |
|---|------|-----|-----|---------|------------------|
| 6.1 | 1 kΩ 1 % 0603 | Yageo RC0603FR-071KL | 4 | ESP32 GPIO series R | [LCSC C25804](https://www.lcsc.com/product-detail/C25804.html) |
| 6.2 | 100 kΩ 1 % 0603 | Yageo RC0603FR-07100KL | 4 | CTRL pin pull-down | [LCSC C25866](https://www.lcsc.com/product-detail/C25866.html) |

---

## 7. Power input

| # | Part | MPN | Qty | Buy link |
|---|------|-----|-----|----------|
| 7.1 | 24 V / 1.5 A / 36 W enclosed PSU | Mean Well LRS-35-24 | 1 | [Probots IN](https://probots.co.in/smps-metal-power-supply-24v-1-2a-36w-lrs-35-24-mean-well.html) · [Sunrom](https://www.sunrom.com/p/mean-well-lrs-35-series) · [Evelta IN](https://evelta.in/mean-well-lrs-35-24) |
| 7.2 | 24 V → 5 V isolated DC-DC, 2 W | Mean Well IRM-02-5 | 1 | [Sunrom](https://www.sunrom.com/p/irm-02-5) · [DigiKey IN](https://www.digikey.in/en/products/detail/mean-well/IRM-02-5) · [Element14 IN](https://in.element14.com/mean-well/irm-02-5) |
| 7.3 | 3.3 V LDO regulator, SOT223 | Diodes AMS1117-3.3 | 1 (+1 spare) | [LCSC C6186](https://www.lcsc.com/product-detail/C6186.html) |
| 7.4 | 2 A / 250 V slow-blow fuse, 5 × 20 mm | Littelfuse 0215002.MXP | 1 (+2 spares) | [LCSC C190099](https://www.lcsc.com/product-detail/C190099.html) · [DigiKey IN](https://www.digikey.in/en/products/detail/littelfuse/0215002-MXP) |
| 7.5 | PCB-mount fuse clip, 5 × 20 mm | Keystone 3527 | 2 (+2 spares) | [LCSC C92413](https://www.lcsc.com/product-detail/C92413.html) |
| 7.6 | 24 V → 12 V buck module, U10 (LM2596S, 3 A, input ≤ 40 V) — colour-channel rail; **set pot to 12.0 V before install** | Generic LM2596S module | 1 (+1 spare) | [Robu](https://robu.in/product/lm2596s-dc-dc-buck-converter-power-supply/) · [Quartz Components](https://quartzcomponents.com) |

---

## 8. Connectors / panel-mount hardware

| # | Part | MPN | Qty | Buy link |
|---|------|-----|-----|----------|
| 8.1 | 2.1 mm DC barrel jack, panel mount | Generic CP-20235NH | 1 | [Robu](https://robu.in/product/dc-power-jack-female-panel-mount-2-1mm/) · [Quartz Components](https://quartzcomponents.com) |
| 8.2 | SPST 3 A rocker switch, panel mount | Marquardt 1801.1101 | 1 | [Robu](https://robu.in/product/rocker-switch-2-pin-on-off-3a-250v/) · [Quartz Components](https://quartzcomponents.com) |
| 8.3 | 22 AWG silicone wire (red, black, assorted) | Generic | 2 m | [Robu](https://robu.in/product/22awg-silicone-wire/) · [Amazon IN](https://www.amazon.in) |
| 8.4 | Pin header, 2.54 mm, male, breakaway 1×40 (board-joint headers J8–J13: 2× 1×12 + 4× 1×10 — pin 2 of every joint is +12V — plus U10 LM2596 module header 1×4) | Generic | 2 strips (+1 spare) | [Robu](https://robu.in/product/2-54mm-male-pin-header/) · [Quartz Components](https://quartzcomponents.com) |
| 8.5 | Jumper harness, female–female DuPont 2.54 mm, 22 AWG (1× 12-wire B1–B2, 2× 10-wire B2–B3 / B3–B4) | Generic (or solder 22 AWG wires directly) | 3 harnesses | [Robu](https://robu.in/product/jumper-wires-female-female/) · [Amazon IN](https://www.amazon.in) |

---

## 9. Controller

| # | Part | MPN | Qty | Buy link |
|---|------|-----|-----|----------|
| 9.1 | ESP32-C3 SuperMini dev board | Espressif ESP32-C3 SuperMini | 1 | [Robu IN](https://robu.in/product/esp32-c3-supermini-development-board/) · [Amazon IN](https://www.amazon.in/s?k=ESP32-C3+SuperMini) |

---

## 10. PCB (made-to-order)

| # | Part | Manufacturer | Qty | Buy link |
|---|------|--------------|-----|----------|
| 10.1 | V0 driver PCBs (FR4, 2-layer, 1 oz Cu) — **4 separate boards from the 2026-09-12 split**: B1 150.5 × 20, B2 149 × 20, B3 97.9 × 20, B4 175.1 × 20 mm | JLCPCB | 5 each (min MOQ) | [JLCPCB](https://jlcpcb.com) — order `hardware/kicad_project/aquarium_v0_board{1..4}.kicad_pcb` |
| 10.2 | LED MCPCB (Al-core, 140 × 20 mm, 5-LED board × 2 designs, 1.6 mm, white soldermask) | JLCPCB or Indian fab | 2 designs × 4 (+2 spares) | [JLCPCB](https://jlcpcb.com) · [PCBWay](https://www.pcbway.com) · [PCBPower IN](https://www.pcbpower.com) |

> **Note**: V0 KiCad project file (`hardware/kicad_project/aquarium_v0.kicad_pro`) is not yet created. The PCB cannot be ordered until the schematic + layout are done.

---

## 11. Mechanical / chassis

| # | Part | Spec | Qty | Buy link |
|---|------|------|-----|----------|
| 11.1 | Aluminium extrusion 6063-T5, 80 × 20 mm, cut to 600 mm | Local hardware | 1 | Local aluminium extrusion shop (search "6063 aluminium extrusion 80×20") · [Robu IN](https://robu.in) · [Probots IN](https://probots.co.in) |
| 11.2 | Thermal interface pad, 3 W/mK, 0.5 mm thick (cut to 140 × 20 mm × 4) | Bergquist GP1500 or generic | 1 sheet | [Robu IN](https://robu.in/product/thermal-pad/) · [Amazon IN](https://www.amazon.in/s?k=thermal+pad+3W%2FmK) |
| 11.3 | Opal acrylic diffuser sheet, 3 mm, 600 × 80 mm | Cast acrylic, opal | 1 | Local plastic supplier · [SimplyAcrylic IN](https://www.simplyacrylic.com) · [IndiaMART](https://www.indiamart.com) |
| 11.4 | End caps (3D-printed PETG, OR aluminium machined) | — | 2 | Local 3D print service · [Imaginarium IN](https://www.imaginarium.io) · [Objectify IN](https://objectify.co.in) |
| 11.5 | Adjustable rim-mount brackets, stainless steel | 10-25 mm rim range | 2 | [Amazon IN](https://www.amazon.in/s?k=aquarium+light+bracket) · Local aquarium supply |
| 11.6 | M3 × 6 mm cap screws (MCPCB → extrusion) | Stainless | 16 | Local hardware |
| 11.7 | M3 × 8 mm cap screws (end caps → extrusion) | Stainless | 4 | Local hardware |
| 11.8 | M3 × 5 mm standoff + screw (driver PCBs — 2 per board × 4 boards) | Nylon or brass | 8 | [Robu IN](https://robu.in) |

---

## 12. Assembly consumables

| # | Part | Qty | Buy link |
|---|------|-----|----------|
| 12.1 | Solder wire (Sn63/Pb37 or lead-free), 100 g | 1 | [Robu IN](https://robu.in) · local electronics shop |
| 12.2 | Solder flux paste, 50 g | 1 | [Robu IN](https://robu.in) |
| 12.3 | Isopropyl alcohol (IPA), 250 ml | 1 | [Amazon IN](https://www.amazon.in/s?k=isopropyl+alcohol) |
| 12.4 | Lint-free wipes | 1 pack | [Amazon IN](https://www.amazon.in/s?k=lint+free+wipes) |
| 12.5 | Heat-shrink tubing assortment | 1 | [Robu IN](https://robu.in) |
| 12.6 | M3 tap + tap handle | 1 | Local hardware |

---

## 13. Tools required (one-time, if you don't have them)

| # | Tool | Approx ₹ | Buy link |
|---|------|-----------|----------|
| 13.1 | Digital multimeter (with mA range) | 1,000–3,500 | [Amazon IN](https://www.amazon.in/s?k=digital+multimeter) — Mastech MS8233E or Fluke 101 |
| 13.2 | Bench DC PSU (24 V, current-limited) | 3,500–8,000 | [Amazon IN](https://www.amazon.in/s?k=bench+dc+power+supply) — MCH-K305D |
| 13.3 | Oscilloscope (≥ 50 MHz, 2 channels) | 5,000–20,000 | [Amazon IN](https://www.amazon.in/s?k=oscilloscope) — Hantek DSO5102P or Rigol DS1054Z |
| 13.4 | Soldering iron (60 W min, temp-controlled) | 1,500–4,000 | [Robu IN](https://robu.in/product/ts100-soldering-iron/) · [Amazon IN](https://www.amazon.in/s?k=soldering+iron) |
| 13.5 | Side cutters + tweezers | 300–600 | [Robu IN](https://robu.in) |
| 13.6 | K-type thermocouple + meter | 2,000–3,000 | [Amazon IN](https://www.amazon.in/s?k=k+type+thermocouple) — Mastech MS6501 |

---

## 14. Order checklist — what to buy NOW (Phase B)

**Order in one LCSC cart** (≥ $50 for free shipping to India):
- 10× AL8860W6-7 (C460356)
- 10× SS3100 (C2480)
- 10× Würth 68 µH (C184706)
- 10× 22 µF 1210 (C13753)
- 100× 100 nF / 50 V / 0603 (C346191)
- 20× 1 µF / 50 V / 0805 (C28323)
- 10× WSL 0.40 Ω (C2990117)
- 5× WSL 0.82 Ω (C2990150)
- 3× WSL 0.33 Ω (C2990101)
- 20× 1 kΩ 0603 (C25804)
- 20× 100 kΩ 0603 (C25866)
- 5× 2 A fuse (C190099)
- 4× fuse clip (C92413)
- 5× AMS1117-3.3 (C6186)

**Order separately from Indian distributors**:
- 1× Mean Well LRS-35-24 → Probots / Sunrom / Evelta
- 1× Mean Well IRM-02-5 → Sunrom / DigiKey / Element14
- 1× Nichicon UPW1H221MPD 220 µF → Element14 IN / Mouser IN
- 1× ESP32-C3 SuperMini → Robu IN
- 1× DC barrel jack 2.1 mm → Robu IN
- 1× rocker switch → Robu IN
- 2 m 22 AWG silicone wire → Robu IN

**Local hardware**:
- 1× aluminium extrusion 6063, 600 mm cut
- 1× thermal pad 3 W/mK
- 1× opal acrylic sheet 600 × 80 × 3 mm
- 2× stainless brackets
- M3 fasteners

**Total estimated cost for prototype (qty 1)**: ₹3,500–4,000 (matches BOM).

---

## 15. Source-by-source quick links

### LCSC (cart above, ≈ ₹1,720 + shipping)
- [lcsc.com](https://www.lcsc.com)

### DigiKey India
- [digikey.in](https://www.digikey.in)

### Mouser India
- [mouser.in](https://www.mouser.in)

### Element14 / Farnell India
- [in.element14.com](https://in.element14.com)

### Indian Mean Well distributors
- [Sunrom](https://www.sunrom.com)
- [Evelta](https://evelta.in)
- [ConvertersIndia](https://www.convertersindia.com)
- [Probots](https://probots.co.in)

### Indian generic electronics
- [Robu.in](https://robu.in) — ESP32, brackets, switches, jacks, thermal pads
- [Quartz Components](https://quartzcomponents.com) — connectors, switches
- [PCBPower](https://www.pcbpower.com) — Indian MCPCB fab (Bangalore)
- [LionCircuits](https://www.lioncircuits.com) — Indian PCB fab (Bangalore)

### Local sources (city-dependent)
- Aluminium extrusion: any local hardware / aluminium shop
- Acrylic diffuser: local plastic / acrylic sheet supplier
- Mounting brackets: aquarium supply shop, Amazon IN, IndiaMART
- 3D print (end caps): local 3D print service or [Imaginarium](https://www.imaginarium.io), [Objectify](https://objectify.co.in), [3Ding](https://www.3ding.in)

---

## 16. What is NOT in this list

- **TICA Color Up** (for comparison test in TP-03): buy from Amazon IN / Flipkart / aquarium shop, ≈ ₹4,500–5,500
- **Spectrometer** (for TP-05): defer to V1; budget option [HiPeak AS8030](https://www.amazon.in/s?k=HiPeak+AS8030) ≈ ₹12,000
- **Smart plug** (for TP-07 reliability soak): [Tapo P110](https://www.amazon.in/s?k=Tapo+P110) or Wipro 16A ≈ ₹1,500

These are test-only purchases, not part of the light itself.
