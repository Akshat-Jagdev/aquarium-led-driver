# Mechanical Assembly — V0 Light (60 cm)

> How the parts fit together for a 60 cm V0 build:
> 4 MCPCBs (2 designs), opal diffuser, rim-mount bracket, passive cooling.

## 1. Exploded view (text)

```
       ┌─────────────────────────────────────────────────┐
       │              Opal acrylic diffuser (600×80×3mm) │  (1)
       └─────────────────────────────────────────────────┘
                            │ clips into
                            ▼
       ┌─────────────────────────────────────────────────┐
       │  Aluminium extrusion 6063-T5 (600 × 80 × 20 mm) │  (2)
       │   ┌──────────────────────────────────────┐      │
       │   │  4× MCPCB (140 × 20 mm) thermal pad │      │  (3)
       │   └──────────────────────────────────────┘      │
       │   ┌──────────────────────────────────────┐      │
       │   │ Driver PCB (14 mm strip, in cavity)  │      │  (4)
       │   └──────────────────────────────────────┘      │
       └─────────────────────────────────────────────────┘
            ▲                                ▲
            │                                │
       Left end cap                     Right end cap
       (5)                              (5)
            ▲                                ▲
            │ rim-mount bracket ──────────────┘
            │ (6)
```

## 2. Bill of materials (mechanical)

| # | Part | Qty | Material | Source |
|---|------|-----|----------|--------|
| 1 | Opal acrylic diffuser, 600 × 80 × 3 mm | 1 | Cast acrylic | Local plastic supplier (Pune/Mumbai/Bangalore) |
| 2 | Aluminium extrusion, 600 mm × 80 × 20 mm | 1 | 6063-T5 | Local hardware, Robu, Probots |
| 3 | MCPCB, 5-LED array, 140 × 20 mm — 2 designs **B** and **DR** | 2 each | Aluminium-core PCB | JLCPCB / Indian fab |
| 4 | Driver PCBs — 4 boards (2026-09-12 split): B1 150.5×20, B2 149×20, B3 97.9×20, B4 175.1×20 mm | 4 | FR4 + copper | JLCPCB / PCBWay |
| 5 | End caps | 2 | Aluminium or 3D-printed PETG | Local |
| 6 | Rim-mount bracket, adjustable | 2 | Stainless steel 304 | Local aquarium supplier |

Plus fasteners:
- **16×** M3 × 6 mm cap screw (MCPCB to extrusion, 4 per board)
- 4× M3 × 8 mm cap screw (end caps to extrusion)
- **8×** M3 × 5 mm standoff + screw (driver boards — 2 per board)
- 3× jumper harness, female–female 2.54 mm (B1–B2 12-wire, B2–B3 and
  B3–B4 10-wire each) + 6× pin headers J8–J13 fitted to the boards
  (see `pcb_layout_notes.md` §3.4)
- 2× M3 × 8 mm screw + wing-nut (bracket to extrusion slot)
- 4× M3 nut for above
- 4× #4 × 6 mm self-tap (MCPCB thermal pad retainer, optional)

## 3. Step-by-step assembly

### 3.1 Driver PCB prep
1. Populate the 7 AL8860 channels (see schematic text §3).
2. Populate ESP32 interface passives (1 kΩ, 100 kΩ).
3. Populate input section: fuse clips, DC jack footprint, rocker switch,
   220 µF electrolytic, 100 nF X7R.
4. Populate 24V → 5V → 3.3V: IRM-02-5 + AMS1117-3.3 with 1 µF caps.
5. Visually inspect, then **TP-02 (full PCB bench test)** before mounting.

### 3.2 Extrusion prep
1. Cut extrusion to 600 mm (±1 mm).
2. Deburr both ends with a file.
3. Drill **8× M3 mounting holes** for the 4 driver boards (2 per board
   — per-board hole map in `extrusion_dims.md` §0.1; x positions in the
   580 mm frame: 20, 112, 190, 290, 330, 390, 495, 560 mm).
4. Drill 2× M3 holes at each end for the end caps.
5. If using slot profile, drill the LED-cable pass-through at one end
   (~Ø 6 mm).
6. Wipe clean with isopropyl alcohol.

### 3.3 LED MCPCB mounting
1. Cut 4 pieces of thermal pad to **140 × 20 mm** (one per MCPCB).
2. Peel protective film from one side of the thermal pad, stick to the
   80 mm face of the extrusion at the marked positions (end-to-end,
   ~2 mm gaps, centred).
3. Peel the other protective film, place the MCPCB on top, align the
   5 LED pads (3 white + red + colour) with the board pad pattern —
   boards L1, L2 (blue) go on the left half; boards R1, R2 (deep-red)
   on the right half.
4. Fasten with **4× M3 × 6 mm screws per board** through the MCPCB
   corner holes into the extrusion (drill + tap M3 first if the
   extrusion wall is too thick to self-tap reliably; aluminium 6063 is
   soft enough to self-tap with care).
5. Repeat for all 4 MCPCBs = **16 screws total**.

### 3.4 LED wiring
1. Solder 22 AWG silicone wire from each MCPCB to its header (J2–J5):
   **6 wires per board** — white anode/cathode, red anode/cathode,
   colour anode/cathode.
2. Use red wire for anode, black for cathode (consistency).
3. The red / blue / deep-red series chains are completed on the **driver
   PCB** (short traces between headers) — no daisy-chain wires between
   MCPCBs. Boards must plug into J2, J3, J4, J5 **in order**
   (L1, L2, R1, R2) so the red chain is unbroken.
4. Keep wire lengths equal so the 4 MCPCBs are visually symmetric.

### 3.5 Driver board mounting
1. Lay the 4 populated driver boards flat on the channel web beside the
   MCPCBs (each board's J2–J5 header next to its own MCPCB — see
   `extrusion_dims.md` §0.1 for the seam-gap and mounting map).
2. Secure each board with its 2× M3 standoffs (8 total).
3. Connect the 4 MCPCB headers (J2–J5) — boards must sit in order
   B1, B2, B3, B4 (the red chain is series through all four).
4. Connect the 3 jumper harnesses across the seams (J8↔J9 12-wire,
   J10↔J11 and J12↔J13 10-wire — pin map `pcb_layout_notes.md` §3.4).
   ⚠ Check header-pin + harness height against the diffuser seat
   before final seating (flange-clearance flag, `extrusion_dims.md`
   §0.1).
5. Connect the ESP32 header (J6) — ESP32 sits externally for V0
   (USB accessible).

### 3.6 Diffuser mounting
1. Slide the opal acrylic sheet into the slot on the 80 mm face.
2. If no slot, hold in place with 4× small plastic clips at the ends and
   middle (custom 3D printed).
3. Diffuser should sit ~5 mm above the LED MCPCBs to allow light
   mixing.

### 3.7 End caps
1. Slide end caps onto both ends of the extrusion.
2. Secure with M3 × 8 mm screws.
3. Leave a small (~2 mm) drain slot in the bottom of each end cap so
   any condensation can escape.

### 3.8 Bracket mounting
1. Slide the rim-mount bracket base into the bottom slot of the
   extrusion (or attach via the end cap screws — design-specific).
2. Adjust the bracket width to match the aquarium rim (10–25 mm
   range).
3. Tighten the thumb screws so the bracket grips the rim firmly but
   without bending.

### 3.9 Final inspection checklist

- [ ] All 4 MCPCBs firmly screwed down (16 screws), no rocking.
- [ ] All LED wires soldered, no cold joints, no shorts to extrusion.
- [ ] Colour chains complete: boards plugged in L1→L2→R1→R2 order.
- [ ] Diffuser clicks into place, no gap to extrusion.
- [ ] End caps flush, screws tight.
- [ ] Bracket grips rim, light does not wobble.
- [ ] DC barrel jack and rocker switch accessible without removing
      brackets.
- [ ] **Run TP-04 (thermal 2-hour soak) before mounting on a tank.**

## 4. Tooling list

- Soldering iron (60 W min, temp-controlled) + lead-free or Sn63/Pb37
  solder
- Side cutters, tweezers
- M3 tap + tap handle
- 2.5 mm and 3 mm drill bits
- Hand drill or drill press
- Files + deburring tool
- Multimeter
- Isopropyl alcohol + lint-free wipes
- Torque driver (optional, 0.6 N·m for M3 into aluminium)
- Phillips #1 and #0 screwdrivers

## 5. Weight budget

| Item | Mass (g) |
|------|----------|
| Extrusion (hollow, 600 mm length) | 240 |
| Driver PCB + components | 80 |
| 4× MCPCB | 60 |
| LEDs | 10 |
| Diffuser | 170 |
| End caps (aluminium) | 50 |
| Brackets | 100 |
| Wires + misc | 30 |
| **Total** | **~740 g** |

Light enough for any 10 mm rim to support; check rim thickness before
final install.
