# 🛒 SHOPPING LIST: NOT PURCHASED
**Project**: Aquarium V0 / ColorBoost — prototype (qty 1)
**Generated**: 2026-09-07
**Source of truth**: `LCSC_TRUTH_BOM.csv` (LCSC order) + `PARTS_LIST.md` (Sept 4)

> Items you will buy from **LCSC** are listed in `LCSC_TRUTH_BOM.csv` (drivers, diodes,
> inductors, all SMD passives, the 220 µF electrolytic, and the LCSC-sourced LEDs).
> LEDs (20×), the Mean Well LRS-35-24 PSU, and the ESP32-C3 are **already owned**.
> Everything else is below.

---

## 1. Add to your LCSC cart (on LCSC, but missing from LCSC_TRUTH_BOM.csv)

| ☐ | Item | MPN | Qty | LCSC Part # |
|---|------|-----|-----|-------------|
| ☐ | 3.3 V LDO regulator, SOT-223 | AMS1117-3.3 | 2 (1 + spare) | C6186 |
| ☐ | 2 A / 250 V slow-blow fuse, 5 × 20 mm | Littelfuse 0215002.MXP | 3 (1 + spares) | C190099 |
| ☐ | PCB-mount fuse clip, 5 × 20 mm | Keystone 3527 | 4 | C92413 |

## 2. Indian distributors (order online)

| ☐ | Item | MPN | Qty | Supplier |
|---|------|-----|-----|----------|
| ☐ | ~~24 V → 5 V isolated DC-DC, 2 W~~ **NOT NEEDED FOR V0** — the IRM-02-5 is an 85–264 VAC input part and cannot convert 24 VDC; V0 ships with U8/U9/C3/C4 unpopulated and the ESP32 USB-powered (see `hardware/mechanical/pcb_layout_notes.md` §2.7 item 13). Buy a real 24 V→5 V buck instead for V1: e.g. Recom R-78E5.0-0.5 | ~~Mean Well IRM-02-5~~ → Recom R-78E5.0-0.5 (V1) | 1 | [element14 IN](https://in.element14.com/recom-power/r-78e5.0-0.5) · LCSC |

## 3. Robu.in / Amazon IN / local electronics

| ☐ | Item | Spec | Qty | Supplier |
|---|------|------|-----|----------|
| ☐ | DC barrel jack, panel mount | 2.1 mm | 1 | Robu · Amazon IN |
| ☐ | Rocker switch, panel mount | SPST 3 A | 1 | Robu · Quartz Components |
| ☐ | Silicone hookup wire | 22 AWG, assorted | 2 m | Robu · Amazon IN |

## 4. PCBs — JLCPCB (routed 2026-09-12 — 4 driver boards, ready to order)

| ☐ | Item | Spec | Qty | Supplier |
|---|------|------|-----|----------|
| ☐ | Driver PCBs — 4 separate boards (2026-09-12 split) | FR4, 2-layer, 1 oz Cu: B1 150.5×20, B2 149×20, B3 97.9×20, B4 175.1×20 mm (`hardware/kicad_project/aquarium_v0_board{1..4}.kicad_pcb`) | 5 each (min MOQ) | JLCPCB |
| ☐ | LED MCPCB | Al-core, 140 × 20 mm, 1.6 mm, 2 designs (B / DR), white mask | 4 + 2 spares | JLCPCB · PCBPower IN |

## 4a. Board-joint connectors (new with the split — see `pcb_layout_notes.md` §3.4)

| ☐ | Item | Spec | Qty | Supplier |
|---|------|------|-----|----------|
| ☐ | Male pin header, 2.54 mm, breakaway 1×40 (cut 2× 12-pin for J8/J9 + 4× 10-pin for J10–J13) | Vertical, brass | 2 strips (+1 spare) | Robu · Quartz Components · local |
| ☐ | Female–female DuPont jumper harness, 22 AWG (1× 12-wire B1–B2, 2× 10-wire B2–B3 / B3–B4); or solder 22 AWG silicone wire directly | ≥22 AWG for the +24V/GND pairs (~1.5 A) | 3 harnesses | Robu · Amazon IN |

## 5. Mechanical / chassis (local suppliers)

| ☐ | Item | Spec | Qty | Supplier |
|---|------|------|-----|----------|
| ~~☐~~ ✔ | ~~Aluminium extrusion~~ **PURCHASED 2026-09-08** — 3" C-channel profile w/ integrated opal diffuser (replaces this + the diffuser row) | — | 1 | — |
| ☐ | Thermal interface pad | 3 W/mK, 0.5 mm (cut to 140 × 20 × 4) | 1 sheet | Robu · Amazon IN |
| ~~☐~~ ✔ | ~~Opal acrylic diffuser~~ **PURCHASED 2026-09-08** — integrated in the C-channel profile | — | 1 | — |
| ☐ | End caps | 3D-printed PETG or machined alu | 2 | Local 3D print service |
| ☐ | Rim-mount brackets | Stainless, 10–25 mm rim range | 2 | Amazon IN · aquarium shop |
| ☐ | M3 × 6 mm cap screws (MCPCB → extrusion) | Stainless | 16 | Local hardware |
| ☐ | M3 × 8 mm cap screws (end caps) | Stainless | 4 | Local hardware |
| ☐ | M3 × 5 mm standoff + screw (driver PCBs — 2 per board × 4 boards) | Nylon or brass | 8 | Robu |

## 6. Assembly consumables

| ☐ | Item | Qty |
|---|------|-----|
| ☐ | Solder wire (Sn63/Pb37 or lead-free), 100 g | 1 |
| ☐ | Solder flux paste, 50 g | 1 |
| ☐ | Isopropyl alcohol, 250 ml | 1 |
| ☐ | Lint-free wipes | 1 pack |
| ☐ | Heat-shrink tubing assortment | 1 |
| ☐ | M3 tap + tap handle | 1 |

---

**Already owned — do NOT buy:** 20× LEDs · Mean Well LRS-35-24 · ESP32-C3 SuperMini
**Purchasing via LCSC (see `LCSC_TRUTH_BOM.csv`):** AL8860 ×7, SS310 ×7, 68 µH ×7,
22 µF ×7, 100 nF ×14, 1 µF ×7, 220 µF ×1, all RSET + 0603 resistors, LCSC-sourced LEDs