# PCB Layout Notes — V0 Driver Board

> Hard rules for laying out the V0 PCB. These come from the AL8860
> datasheet, the schematic text in `docs/03_schematic_text.md`, and the
> 80 × 20 mm chassis constraint.

## 1. Board outline

- **Form factor — UPDATED (2026-09-12): four separate boards** split at
  the MCPCB seams (the original single 580 × ≤ 20 mm strip was too long
  and expensive to fab). Each board lies flat on the channel web beside
  its MCPCB, joined at assembly by 2.54 mm pin headers (J8–J13) +
  jumper harnesses. All four keep the original absolute x-coordinates
  (one 580 mm frame), so every position below is in that frame:

| Board | File | x-window (mm) | Size (mm) | Contents |
|-------|------|---------------|-----------|----------|
| B1 | `aquarium_v0_board1.kicad_pcb` | 0 – 150.5 | 150.5 × 20 | logic cluster (J1, F1, J7, C2, J6, R1–R8, U8†, U9†, C3†, C4†) + U1/W1 cell + J2 + J8 |
| B2 | `aquarium_v0_board2.kicad_pcb` | 151 – 300 | 149 × 20 | U5/R + U6/B + U2/W2 cells + J3 + J9, J10 |
| B3 | `aquarium_v0_board3.kicad_pcb` | 300.5 – 398.4 | 97.9 × 20 | U3/W3 cell + J4 + J11, J12 |
| B4 | `aquarium_v0_board4.kicad_pcb` | 398.9 – 574 | 175.1 × 20 | U7/DR + U4/W4 cells + J5 + J13 |

† = DNP per the 2026-09-10 V0 power decision (ESP32 USB-powered).
Board seam gaps as routed: **0.5 mm at every seam** (B1–B2, B2–B3,
B3–B4). Split record + joint pin map: §2.9 and §3.4.
- **2-layer, 1 oz copper** (matches the BOM prototype row).
- **Connector side**: B1's west end has the DC barrel jack footprint, fuse
  clips, and rocker switch footprint. Along the boards: 4× 6-pin headers
  (J2–J5) going to the MCPCB LED strings, and 6× joint headers (J8–J13)
  at the seams.
- **Mounting**: 2× M3 standoff holes per board (8 total) — see
  `extrusion_dims.md` §0.1 for the per-board hole map.

> **Cavity fit — UPDATED (2026-09-08):** the purchased 3-inch C-channel
> profile (opal diffuser, 40 mm usable interior width) replaces the
> 80 × 20 hollow slot. Board width target is **≤ 20 mm** to fit alongside
> the 20 mm MCPCBs (Total 40 mm).
> Verify the inductor (7447783680) height fits the 15 mm flange depth;
> the 100 nF still stays within 2 mm of VIN, always.

## 2. Critical placement rules

### 2.1 AL8860 decoupling (per channel)
- **100 nF X7R 0603** within **2 mm** of AL8860 VIN pin (pin 6).
  Keep the trace to VIN shorter than 5 mm. No vias between the cap and
  the pin.
- **22 µF X7R 1210** within **5 mm** of VIN pin, on the same copper
  pour. This is the bulk input cap for the discontinuous input current.

### 2.2 Switching loop (HIGH DI/DT)
The loop `LX → inductor → diode anode → diode cathode → VIN` carries
**all** the switching current at hundreds of mA / ns edges. Keep this
loop **as small as physically possible**:

```
       ┌──────────────────────────────┐
       │   VIN  ●───┐                 │
       │            │                 │
       │       ┌────┴────┐            │
       │       │  AL8860 │            │
       │       │   LX  ●─┼──[L]──┬─── ┼→ LED anode
       │       └────┬────┘        │   │
       │            │             │   │
       │       ┌────┴────┐        │   │
       │       │   D1    │ anode  │   │
       │       │  cathode┴────────┘   │
       │       └─────────┘            │
       └──────────────────────────────┘
```

- All three components (AL8860, L, D1) on the **same side** of the board.
- The catch-diode anode trace **under** the inductor, not around it.
- No signal traces crossing this loop.

### 2.3 Ground
- **Single ground pour on bottom layer**, unbroken.
- The CS pin → RSET → LED cathode → ground path must land on the
  ground pour via a short trace / via, NOT a long thin trace.
- The CTRL pin 100 kΩ pull-down goes to the **same ground pour** as the
  AL8860 GND, not to a separate "signal ground" island.

### 2.4 Thermal copper
- Underneath each AL8860: at least **100 mm²** of copper pour on **both**
  layers, stitched with thermal vias (8–12 vias, 0.3 mm drill, 0.5 mm
  pad).
- 7 AL8860s total (4W + 1R + 1B + 1DR). Each gets its own thermal island
  so heat doesn't couple between drivers.

### 2.5 LED string routing
- LED strings carry up to 250 mA (white). Use **≥ 1 mm wide** traces.
- Anode trace from inductor to MCPCB connector pin.
- Cathode trace from MCPCB connector to RSET → ground.
- Keep anode and cathode traces **close together** to minimise loop area
  (radiated EMI).
- Colour-series traces between headers (J2↔J3↔J4↔J5 for red, J2↔J3 for
  blue, J4↔J5 for deep-red) carry only 120–303 mA — 0.5 mm minimum is
  fine, but keep them adjacent to their partners.

### 2.6 ESP32 section isolation
- The 3.3 V section (ESP32, IRM-02-5, AMS1117-3.3) sits at one **end**
  of the board, separated by at least **10 mm** from the 24 V / LED
  drivers.
- The CTRL traces from ESP32 GPIOs to AL8860s can cross the boundary,
  but route them on the **opposite side** of the board from any 24 V
  switching trace to avoid coupling.

### 2.7 As-built deviations (V0 layout, 2026-09-10)
The routed board (580.0 × 20.0 mm, 2 layers, DRC 0 violations /
0 unconnected, 131 routes + 108 vias + GND zones) meets the rules above
with the following documented deviations:

1. **AL8860WT-7 is high-side — §2.1/§2.3 sense-path picture is
   obsolete, and VIN is pin 5, not pin 6.** The captured netlist
   (TSOT-25, 5 pins) resolved to a high-side topology: pin 5 = +24V
   (VIN); pin 4 (SET/CS) ties to the LED anode net `/x_A`; RSET
   (R10–R16) sits between +24V and pin 4 (high-side sense); the
   inductor is in the string return (L pin1 → SW pin1, L pin2 →
   `/x_K` → header); the internal switch returns via pin 2 to GND.
   Freewheel loop per cell: +24V → D cathode → D anode → SW → L →
   string cathode → string → RSET → +24V, entirely on F.Cu, ≈6 × 5 mm.
   Read the §2.3 sentence as "**+24V → RSET → CS pin**" (≈5 mm,
   1.0 mm trace, no vias). Ground rules unchanged: GND remains the
   switch/thermal return and gets the full B.Cu pour; only RSET's
   return is to +24V.
2. **CTRL bus on B.Cu as a horizontal lane ladder — deviation from
   §2.3 "unbroken bottom pour".** DR y=1.0, B y=1.5, R y=2.0,
   W y=2.5 (W dips to y≈11 near J3/J4), all 0.25 mm, via pairs at the
   R1–R4 fan-out and each driver's pin 3. Accepted: CTRL is a
   high-impedance PWM input (100 kΩ pull-downs R5–R8, 1 kΩ series
   R1–R4) carrying no switching return current, and F.Cu GND islands +
   the west↔east F.Cu bridge stitch over the lanes. Read §2.3 as
   "unbroken pour under every switching loop" — met: every SW/24V
   switching loop sees continuous GND on the opposite layer.
3. **LED cathode traces 0.8 mm vs §2.5 "≥ 1 mm".** Anodes (`/x_A`)
   are 1.0 mm, cathodes (`/x_K`) 0.8 mm (LED_Anode / LED_Cathode
   netclasses). 0.8 mm external 1 oz carries ≈1.6 A at 10 °C rise
   (IPC-2221) vs 250 mA strings — ≈6× margin. 1.0 mm cathodes did
   not fit the 20 mm strip lane budget against 0.3 mm power-class
   clearances. The §2.5 rule should read "anode ≥ 1.0 mm, cathode
   ≥ 0.8 mm".
4. **Colour-chain traces 0.3 mm vs §2.5 "0.5 mm minimum".** The five
   inter-header chains (B_J23, R_J23, R_J34, R_J45, DR_J45;
   120–303 mA DC) are 0.3 mm B.Cu lanes (y ≈ 18.15–19.45, plus an
   east W4_K lane at y=3.9). 0.3 mm carries ≈0.55 A at 10 °C rise —
   ≈1.8× margin even for the 303 mA blue chain. These are DC string
   currents (no di/dt), so width is thermal-only; 0.5 mm did not fit
   the corridors between power-class pads.
5. **Diode anode trace reaches the inductor pad edge, not the body
   mid-span (§2.2).** In each cell the SS3100 sits directly above the
   AL8860; the anode/SW trace drops vertically to the SW junction and
   jogs ≈6 mm along the inductor's pad edge to L pin 1. No detour
   around the inductor; the switching loop stays ≈6 × 5 mm.
6. **Anode/cathode pair proximity (§2.5) — pairs diverge after the
   header escape.** Pairs leave J2–J5 as adjacent 2.54 mm escapes,
   then diverge by design (anode to the RSET row y≈16, cathode to the
   inductor y≈10). The LED current loop closes off-board through the
   MCPCB string, so loop area is dominated by the header-to-MCPCB
   wiring; the rule is satisfied at the header escape.
7. **Thermal islands: 5–6 stitching vias per island, not the 8–12 of
   §2.4 — but 63 GND vias total (~9/driver).** The 20 mm strip and
   the K/A lane corridors on B.Cu left room for 5–6 vias per 12 × 8 mm
   F.Cu island; U6/U4 islands get 3 each. The global count (63 GND
   vias, all 0.5/0.3 mm) exceeds the 8-per-driver floor, every island
   fill bonds to the B.Cu pour, and the B.Cu pour itself (7371 mm²)
   is the dominant heat spreader. Read §2.4 as "≥8 vias per driver
   across both layers" — met.
8. **Island east edge extended to x0+28.4** (beyond the cell's
   nominal boundary): the F.Cu islands reach past the 22 µF caps' pin-1
   GND pads so the fill bonds them where a via-in-pad would land on
   B.Cu corridors sealed by the J4/J5 pad rows.
9. **B.Cu pour topology (4 fill islands, all connected).** The pour
   (y0.5–16.5, x0.5–579.5) is split by the CTRL via_B return fence
   into a west fragment (x0.5–73.5) and east main (x76–579.5),
   stitched by a dedicated F.Cu GND bridge (tie track + vias at
   (72.4,16.2) west and (99.9,14.5) east). Two small CTRL "snake"
   pockets (x171–212 and x212–414, y1.3–10.7) contain no GND items
   and are harmless. R5–R8 pin 1 and C25/C23/C12/C13 pin 1 GND pads
   bond via a 0.3 mm F.Cu tie track at y18 and/or island fill instead
   of via-in-pads (their via spots sit in sealed B.Cu pockets / on K
   descents).
10. **Footprint Datasheet/Description fields carry deterministic
    placeholder text** ("see schematic symbol" / the footprint id) —
    required for byte-reproducible `gen_pcb.py` regeneration; they do
    not affect the electrical design.
11. **Inductor footprint corrected (2026-09-10): L1–L7 use
    `Inductor_SMD:L_7.3x7.3_H3.5`, not `L_12x12mm_H8mm`.** The BOM,
    procurement plan, and `docs/03_schematic_text.md` all pin the
    Würth **7447783680** (WE-PD 7332: 7.4 × 7.3 mm, 3.5 mm max
    height, land-pattern pads ±3.2 mm, 1.5 × 2.2 mm — per the Würth
    datasheet). The originally-captured `L_12x12mm_H8mm` is the
    WE-PD **Typ-LS** land pattern (pads ±4.95 mm, 2.9 × 5.4 mm) —
    the part would not have fit its own pads. Height check: 3.5 mm
    max ≪ 15 mm flange depth. Fixed in `gen_schematic.py`; the 14
    overlay routes landing on L pads (7 SW jogs, 7 K descents) and
    the /B_K, /DR_K, /R_K vias moved ±1.75 mm to follow the pads
    (patch8/patch9).
12. **F.Cu thermal islands are 12.9 × 4.8 mm (62 mm² polygon) vs the
    §2.4 "≥ 100 mm² on both layers".** The 20 mm strip constrains the
    island to the band between the SW/+24V copper (y<7.6) and the
    K/A lane corridors (y>12.4). Per driver the B.Cu pour contributes
    ≈500 mm² of contiguous GND (7376 mm² total over 579 mm ≈ 12.7
    mm² per mm of strip, minus lane corridors), so the two-layer
    total per driver is ≈560 mm² ≫ 100 mm². With 5–6 vias per island
    plus via-in-pads on every SMD GND pad, the thermal resistance is
    dominated by the B.Cu pour, which is unbroken under every cell.
    Read §2.4 as "≥ 100 mm² of GND copper **per driver across both
    layers**, of which the dominant spreader is on the bottom".
13. **V0 build note (decided 2026-09-10): the 5 V rail is not
    populated — U8, U9, C3, C4 are DNP; the ESP32-C3 SuperMini is
    powered from its own USB port.** The captured design feeds +24 V
    into a Mean Well IRM-02-5, but that part requires 85–264 **VAC**
    mains input and cannot convert 24 VDC (the error originates in
    `docs/03_schematic_text.md` §2 "IRM-02-5 (24V → 5V)"). Rather
    than re-spin the power section, V0 uses the docs' own §2
    fallback: USB-powered ESP32 (its onboard regulator drives the
    +3V3 net through J6 pin 6); J6 still carries the four PWM
    signals + GND. The board is fabbed exactly as routed — the DNP
    parts simply stay off. **V1 must replace U8 with a real 24 V→5 V
    DC-DC** (e.g. Recom R-78E5.0-0.5 buck, SIP-3) or the Traco
    TMR 2-2411 isolated module; U9 (AMS1117-3.3) stays for the
    3V3-derivation in that spin.

### 2.8 As-routed architecture snapshot (for the record)
- 250 track segments across 39–40 nets (≈131 overlay routes) +
  108 vias (45 signal + 63 GND), all 0.5 mm pad / 0.3 mm drill
  (JLCPCB minimums); narrowest track 0.25 mm (CTRL).
- Netclasses: Default 0.25/0.2, LED_Anode 1.0/0.3, LED_Cathode
  0.8/0.3, Power_24V 0.5/0.3.
- F.Cu: +24V bus 1.0 mm at y≈2.2 with 0.5 mm branches to VIN pins,
  RSET pads, decoupling caps; per-channel SW/LX loops ≤ 4.4 mm
  segments; 7 GND thermal islands (12 × 8 mm); GND tie/bridge tracks.
- B.Cu: CTRL ladder (see deviation 2); K corridors y=13.2 (B_K,
  DR_K) and y=17.25 (R_K) plus east W4_K lane y=3.9; A lanes
  (R_A y=13.05, B_A y=15.6, DR_A y=15.8, W3_A/W4_A y=15.8); colour
  chains y=18.15–19.45 (/CTRL_DR return lane at y=18.85); GND pour.
- Logic cluster (ESP32, IRM, AMS1117, J1/J6/J7, R1–R8) at x=8–99;
  driver cells at x=121–456 (U1 121, U5 155, U6 196, U2 245, U3 330,
  U7 398, U4 438); minimum adjacent cell spacing 40 mm.
- The board is generated deterministically: `gen_pcb.py` +
  `ROUTES_EXTRA.json` → byte-identical `.kicad_pcb`; verify with
  `verify_pcb.py` (11 checks) and the DRC gate
  (`kicad-cli pcb drc --refill-zones --save-board`).

### 2.9 Split record — 4 boards at the MCPCB seams (2026-09-12)

§2.8 describes the pre-split single-board lineage. As of 2026-09-12 the
580 mm board is **four boards** (§1 table), reworked so that every
seam-crossing net terminates on a pair of joint headers instead of a
long trace. What changed and what was kept:

**Kept unchanged, same absolute coordinates:** all 7 driver cells, the
logic cluster, every J2–J5 escape, all cell-local routing, netclasses,
per-cell F.Cu thermal islands, and the B.Cu CTRL-ladder y-levels.

**Deleted:** every seam-crossing trace — the +24V trunk beyond each
window, CTRL-ladder segments beyond each seam, all five inter-header
colour chains (B_J23, R_J23, R_J34, R_J45, DR_J45), and the seam-crossing
pieces of /R_A, /B_A, /R_K.

**Added:** per-board +24V trunks (y≈1.7–2.2 B.Cu band, shortened to each
board), per-board CTRL segments, and short escapes from each joint
header pin to its net. Final overlay: 195 routes + 72 explicit vias in
`ROUTES_EXTRA.json` (patches 10–27; patch25 fixed the B4 chain
crossings, patch26/27 fixed the B1 /B_A joint escape — see below).

**Joint headers (all rot −90, pin 1 east, along the south edge):**
J8 (129.71, 18.55) ↔ J9 (210.50, 18.55) are 1×12; J10 (296.0) ↔ J11
(327.0), J12 (395.8) ↔ J13 (448.5) are 1×10. Pin maps in §3.4. ~1.5 A
total load crosses each seam on pins 1–2 (two pins parallel, within
2.54 mm header ratings).

**/B_A joint-escape width fix (patch26/27).** The J8 pin-9 escape was
routed 0.5 mm (a copy-paste from a CTRL-width escape); `/B_A` is
netclass LED_Anode → 1.0 mm. Widening in place failed DRC (the F.Cu
column cannot thread the 1.075 mm corridor between the /R_A and /W1_A
columns), so the ascent moved to B.Cu: lane y12.2 extended to x109.39,
up on B.Cu to y14.95, via up, straight F.Cu column into J8 pin 9
(clearances 0.30–0.45 mm, hand-checked; the sealed B.Cu pour pocket it
creates contains no GND items and is island-removed).

**Verification (2026-09-12).** Per board: DRC **0 violations / 0
unconnected** (`kicad-cli pcb drc --refill-zones --save-board`) and
`verify_pcb.py --board N` **ALL PASS** (per-board footprint inventory,
pad↔net audit both directions against the one shared `netlist.net`,
DRC gate, copper-inside-outline, MH positions, J2–J5 pin-1/MCPCB-span,
joint-header pin-1, netclass track widths, JLC via minimums, GND pour
fill + ≥8 GND vias/driver). As-built per-board stats:

| Board | fps | vias | GND vias | B.Cu pour |
|-------|-----|------|----------|-----------|
| B1 | 28 | 31 | 15 | 2400 mm² |
| B2 | 23 | 44 | 26 | 1780 mm² |
| B3 | 11 | 26 | 13 | 1305 mm² |
| B4 | 16 | 34 | 17 | 2751 mm² |

Reproducibility: regen ×2 + DRC-gate save → **byte-identical** ×4.
Per-board layer SVGs for eyeball review: `kicad_project/pcb_views/
aquarium_v0_board{N}-{F.Cu,B.Cu,F.Silkscreen,B.Silkscreen,Edge_Cuts}.svg`.

> **Known cosmetic nit:** the joint headers' *courtyards* overhang the
> board south edge by ~0.34 mm (copper is fully inside; DRC
> edge-clearance passes). Fabricators ignore courtyard overhang at the
> board edge.

## 3. Connector pinout

### 3.1 24 V input (DC barrel jack → switch → fuse)
```
J1 (DC barrel, 2.1 mm):
   pin 1 (tip)   → +24 V (through fuse + switch)
   pin 2 (shell) → GND
```

### 3.2 MCPCB headers (one header per MCPCB, J2–J5)

Each MCPCB carries a 5-LED array — 3 white + 1 red + 1 colour — per the
arrangement in `extrusion_dims.md` §3. String topology:

- **White**: each board's 3 whites in series on-board → its own AL8860
  (250 mA). No cross-board white wiring.
- **Red**: 4 LEDs in series ACROSS all four boards (R_L1 → R_L2 → R_R1 →
  R_R2), one driver (120 mA).
- **Blue**: 2 LEDs in series across boards 1–2, one driver (303 mA).
- **Deep-red**: 2 LEDs in series across boards 3–4, one driver (120 mA).

So each board needs 6 connections (white pair, red pair, colour pair).
The colour series chains are completed on the **driver PCB** with short
traces between the headers:

```
J2 (MCPCB1=L1), J3 (MCPCB2=L2) — colour = BLUE:
   pin 1 → W_A   white string anode   (white LX, feeds 3× white in series)
   pin 2 → W_K   white string cathode → RSET 0.40 Ω → GND
   pin 3 → R_A   red LED anode        (red LX / previous board R_K)
   pin 4 → R_K   red LED cathode      → next board R_A
   pin 5 → B_A   blue LED anode       (blue LX / other board B_K)
   pin 6 → B_K   blue LED cathode     → other board B_A (PCB trace J2↔J3)

J4 (MCPCB3=R1), J5 (MCPCB4=R2) — colour = DEEP-RED:
   pins 1–4 identical to J2 (white + red chain).
   pin 5 → DR_A  deep-red anode       (deep-red LX / other board DR_K)
   pin 6 → DR_K  deep-red cathode     → other board DR_A (PCB trace J4↔J5)
```

The red chain runs J2→J3→J4→J5 through the R_A/R_K traces, so boards must
be connected in order L1(J2), L2(J3), R1(J4), R2(J5).

### 3.3 ESP32 header (J6)

```
J6 (1×6 pin, 2.54 mm):
   pin 1 → GPIO0 (white CTRL)
   pin 2 → GPIO1 (red CTRL)
   pin 3 → GPIO2 (blue CTRL)
   pin 4 → GPIO3 (deep-red CTRL)
   pin 5 → GND
   pin 6 → 3V3 (powers ESP32, optional)
```

### 3.4 Board-joint headers (J8–J13, added by the 2026-09-12 split)

One pin header at each end of every seam, mated by a female–female
jumper harness (§2.9). Pin 1 is the east/rightmost pin. Identical pin
map at both ends of each joint:

```
J8 (B1) ↔ J9 (B2) — 1×12:
   pin 1  → +24V      pin 2  → +24V     (power, 2 pins parallel)
   pin 3  → GND       pin 4  → GND
   pin 5  → /CTRL_W   pin 6  → /CTRL_B
   pin 7  → /CTRL_R   pin 8  → /CTRL_DR
   pin 9  → /B_A      pin 10 → /R_A     (blue + red chain starts)
   pin 11 → /B_J23    pin 12 → /R_J23

J10 (B2) ↔ J11 (B3) — 1×10:
   pin 1  → +24V      pin 2  → +24V
   pin 3  → GND       pin 4  → GND
   pin 5  → /CTRL_W   pin 6  → /CTRL_DR
   pin 7  → /R_J34    pin 8  → /R_K     (R_K passes through B3 to B4)
   pin 9, 10: NC

J12 (B3) ↔ J13 (B4) — 1×10:
   pin 1  → +24V      pin 2  → +24V
   pin 3  → GND       pin 4  → GND
   pin 5  → /CTRL_W   pin 6  → /CTRL_DR
   pin 7  → /R_J45    pin 8  → /DR_J45
   pin 9  → /R_K      pin 10 → /DR_A
```

- CTRL_B and CTRL_R terminate on B2 (their drivers are U6/U5), so they
  only appear on the J8↔J9 joint; /CTRL_W and /CTRL_DR continue across
  all seams.
- Harness: **1× 12-wire (B1–B2) + 2× 10-wire (B2–B3, B3–B4)**,
  female–female 2.54 mm DuPont; use ≥22 AWG wires for the pin 1–2
  power pair (~1.5 A).
- Assembly order is unchanged: connect boards in order B1→B2→B3→B4
  (the red chain is series through all four).

## 4. Things to avoid

| Don't | Why |
|-------|-----|
| Put the input cap on the opposite side from AL8860 | Adds via inductance, breaks the bypass |
| Run CTRL traces next to the LX switching node | Capacitive coupling will inject ripple into CTRL → LED flicker |
| Use a thin ground trace for CS RSET | 250 mA × 0.4 Ω = 100 mV of sense error from a 40 mΩ ground trace |
| Star-route grounds from multiple AL8860s to a single point | A single solid pour is better for buck converters |

## 5. DRC reminders

- Min trace / space: **0.15 mm / 0.15 mm** (JLCPCB default).
- Min via drill: **0.3 mm**.
- Min via pad: **0.5 mm**.
- Edge clearance: **0.3 mm**.
- Silk on the LED connectors: mark + (anode) and − (cathode).
- Copper-to-edge: **0.3 mm** keep-out for the board edge.
