# Aluminium Extrusion — 6063-T5 Heatsink / Housing

> Spec for the V0 chassis: 600 mm × 80 mm × 20 mm aluminium extrusion
> that doubles as the LED heatsink and the outer shell.

## 0. ⚠ UPDATE 2026-09-08 — PROFILE PURCHASED: 3-inch C-channel with opal diffuser

The planned 80 × 20 hollow-slot extrusion has been **replaced by a
purchased 3-inch (~76 mm) C-channel aluminium profile with an integrated
opal diffuser**. This supersedes §1–§2 below where they conflict.

**What changes:**
- ✅ **Opal diffuser** — now part of the profile (delete the separate
  3 mm opal acrylic sheet from the BOM; both items struck off the
  shopping list 2026-09-08).
- ✅ **MCPCB mounting** — boards bolt to the flat web (back) of the
  C-channel; LEDs face the snap-on opal diffuser. 76 mm web width fits
  the 140 × 20 mm boards plus the driver strip **side-by-side**.
- 🔄 **Driver strip width** — the ≤ 14 mm hard constraint came from the
  80 × 20 profile's ~76 × 16 mm enclosed cavity. A C-channel is open, so
  the strip can lie flat on the web and may be widened (e.g. 20–30 mm),
  which eases the 7-channel layout considerably. **Do not finalise the
  KiCad board outline until the channel is measured** (below).
- 🔄 **Thermal mass** — a thin-wall C-channel has less mass than the
  80 × 20 hollow (§4 numbers are optimistic now). TP-04 soak test decides;
  if the web runs hot, add an external strip fin or revert to thicker
  profile for production.
- ❓ **Alloy/temper unknown** — generic C-channel is often 6063 or 6060;
  confirm from seller if thermal numbers (§1) need to hold for
  production. Acceptable for V0 prototype regardless.

**Measured 2026-09-08:** usable interior space ≈ **40 mm** width.
→ Driver strip target width must be **≤ 20 mm** to fit side-by-side with the 20 mm MCPCBs.
Flange height: **15 mm**.
Web thickness: **2 mm**.

### 0.1 Driver strip — 4-board split mounting map (2026-09-12)

The 580 mm driver strip is now **four boards** laid end-to-end on the
web beside the MCPCBs (full split record: `pcb_layout_notes.md` §2.9).
All x positions are in the original 580 mm frame, so they line up with
the MCPCB spans in §3:

```
  x: 0       150.5 151           300 300.5        398.4 398.9       574
     [== B1 150.5 ==][=== B2 149 ===][= B3 97.9 =][== B4 175.1 ==]
      MH1(20,4)              MH2(190,10)    MH3(390,10)  MH4(560,10)
                 MH5(112,11)    MH6(290,10)   MH7(330,4.8)  MH8(495,4.8)
```

- **Seam gaps between boards: 0.5 mm at every seam** (B1–B2, B2–B3,
  B3–B4) — the joint headers (J8–J13, south edge) sit ~60 mm apart
  across each gap and are bridged by female–female jumper harnesses
  (1× 12-wire + 2× 10-wire), routed under/alongside the strip.
- **Mounting: 8× M3 holes total** (2 per board) at MH1 (20, 4), MH5
  (112, 11), MH2 (190, 10), MH6 (290, 10), MH3 (390, 10), MH7 (330, 4.8),
  MH4 (560, 10), MH8 (495, 4.8) — coordinates are (x, y) in the frame
  above; y is from the board's north edge. Update the BOM standoff count
  from 4 to 8.
- ⚠ **Flange-clearance flag — measure before production:** the vertical
  joint-header pins stand **~11.5 mm above the board**, and the boards
  lie flat on the 2 mm web → ~13.5 mm of height, vs the **15 mm**
  flange. The harness wires and connectors add a few mm more, and the
  snap-on opal diffuser seat is above that. **Verify with the diffuser
  seated** that the header pins + harness clear; if tight, route the
  harness flat along the web between the boards, or solder wires directly
  to the headers instead of using DuPont connectors.

**Measure before PCB layout (ruler / vernier):**
1. ~~Interior width between flanges~~ — **≈ 70 mm (measured 2026-09-08)**.
2. **Flange height (channel depth)** — sets available height behind the
   diffuser for LEDs + MCPCB (1.5 mm) + standoffs.
3. **Web (back) thickness** and flange thickness — sets self-tapping
   vs. drilled-and-tapped M3 choice.
4. **Diffuser attachment style** (snap-in lips? friction fit?) — the
   driver strip must not block the diffuser seat.
5. Cut length received (target 600 mm).

## 1. Decision summary

| Property | Value | Why |
|----------|-------|-----|
| Alloy | **6063-T5** | Best thermal conductivity of the common extrudable alloys (200 W/mK), cheapest for custom profiles |
| Cross-section | **80 × 20 mm** | Wide enough for 4× MCPCB in a row, low enough not to dominate the tank silhouette |
| Length | **600 mm** | Fits a 2 ft aquarium rim (≈ 60 cm tank length is the most common Indian tank size) |
| Wall thickness | **1.5–2.0 mm** | Standard for off-the-shelf 80×20 profiles; adequate structural rigidity |
| Finish | **Mill finish (raw)** + anodised option | Mill finish is cheapest; clear anodise gives corrosion resistance for humid environments at +₹60/unit |

## 2. Cross-section sketch

```
          ┌──────────── 80 mm ────────────┐
          │                              │
       20 │  ┌───────────────────────┐   │  20 mm
       mm │  │                       │   │  mm
          │  │   hollow interior     │   │
          │  │   (or solid bar)      │   │
          │  └───────────────────────┘   │
          │                              │
          └──────────────────────────────┘

   Cross-section area for heat spreading = 80 × 20 = 1600 mm²
   Perimeter for convection = 2 × (80 + 20) = 200 mm
```

- **Hollow profile** (typical "80×20 slot") is preferred: it weighs less,
  leaves a wiring channel, and the inner cavity can hold the driver PCB.
- **Solid bar** is acceptable if hollow profile can't be sourced locally
  — adds ~700 g to the assembly.

> **Cavity size**: a standard 80 × 20 slot profile has an interior of
> roughly **76 × 16 mm**. DECIDED (2026-09-01): the driver PCB is a slender
> **≤ 14 mm-wide strip** living in this cavity (`pcb_layout_notes.md` §1).

## 3. LED mounting face — MCPCB arrangement (DECIDED: 4 uniform boards)

The 4 MCPCBs sit on the **80 mm face** (top or bottom depending on
orientation), centred across the width. Two population designs, 4 boards,
all 140 × 20 mm, laid end-to-end:

```
  ←——————— 600 mm extrusion ————————→
  ←17 mm→                          ←17 mm→
        ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐
        │ MCPCB L1  │ │ MCPCB L2  │ │ MCPCB R1  │ │ MCPCB R2  │
        │ W W R W B │ │ W W R W B │ │ W W R W D │ │ W W R W D │
        └───────────┘ └───────────┘ └───────────┘ └───────────┘
        ←—— 140 mm each, 2 mm seams —→   (B = 448 nm, D = 660 nm)
```

- **Board designs**:
  - `L1, L2` (left half): populate **B** = LUXEON Rubix 448 nm.
  - `R1, R2` (right half): populate **D** = LUXEON SunPlus 660 nm.
  - Both designs share the identical 5-pad grid — only the colour pad
    differs. 4 boards = **2× L1/L2 design + 2× R1/R2 design**.
- **LED centres** at 14 / 42 / 70 / 98 / 126 mm from each board's left
  edge → **28 mm pitch**, continuous across board boundaries (seam pitch
  30 mm through the 2 mm gaps — no banding through the opaque diffuser).
- **20 LEDs total:** 12 white + 4 red + 2 blue + 2 deep-red.
- **Mounting:** 4× M3 corner holes per board (**16 total** M3 × 6 mm into
  the extrusion, drilled + tapped).

### Channel / string map (unchanged 7-driver architecture)

| String | Driver | Boards | LEDs in series | I_LED | RSET |
|--------|--------|--------|----------------|-------|------|
| White 1 | AL8860 #1 | L1 | W1,W2,W3 on-board | 250 mA | 0.40 Ω |
| White 2 | AL8860 #2 | L2 | W1,W2,W3 on-board | 250 mA | 0.40 Ω |
| White 3 | AL8860 #3 | R1 | W1,W2,W3 on-board | 250 mA | 0.40 Ω |
| White 4 | AL8860 #4 | R2 | W1,W2,W3 on-board | 250 mA | 0.40 Ω |
| Red      | AL8860 #5 | L1→L2→R1→R2 | R1,R2,R3,R4 across boards | 120 mA | 0.82 Ω |
| Blue     | AL8860 #6 | L1, L2 | B1,B2 across boards | 303 mA | 0.33 Ω |
| Deep red | AL8860 #7 | R1, R2 | D1,D2 across boards | 120 mA | 0.82 Ω |

- **White** strings live entirely on their own board — no cross-board wiring.
- **Red / blue / deep-red** series chains are completed with short traces
  on the **driver PCB** between the J2–J5 headers
  (`pcb_layout_notes.md` §3.2) so the driver board owns every joint.
- **Wiring:** 6 wires per board (white anode/cathode, red anode/cathode,
  colour anode/cathode) to the driver PCB headers.

### Thermal note

Worst board ≈ L1: 3 white at 250 mA (~4.4 W) + 1 red (0.25 W) + 1 blue
(0.96 W) ≈ **5.6 W over 2,800 mm²** (~0.2 W/cm²) — same loading as the
earlier 70 × 20 layout, spread thinner along the bar. The TP-04 2-hour
soak confirms steady state.

## 4. Thermal mass estimate

| Quantity | Value |
|----------|-------|
| Volume of 600 mm of 80×20 hollow (1.5 mm wall) | ≈ 90 cm³ |
| Aluminium density | 2.7 g/cm³ |
| Aluminium mass | ≈ 240 g |
| Specific heat | 0.90 J/g·K |
| Thermal mass | ≈ 220 J/K |

At 22 W continuous, time to rise 20 K from ambient (rough): τ ≈ 220 × 20 / 22 ≈ 200 s.
Soak test (TP-04) of 2 hours is plenty to reach steady state.

## 5. Sourcing notes

- **India**: any local aluminium extruder can cut to length. Common in
  Hyderabad, Pune, Mumbai, Bangalore hardware markets. Search
  "aluminium extrusion 80×20 slot".
- **Online**: Robu, Probots, Evelta stock generic 80×20 profiles in 1 m
  lengths (cut to 600 mm for free or ~₹20).
- **MOQ**: 1 unit for stock profiles; custom profile (with internal
  channels for wiring) needs ~50 unit MOQ and is deferred to V2.

## 6. What to ask the supplier

1. **Alloy**: confirm 6063-T5 (not 6061, not 6005).
2. **Temper**: T5 or T6 — T5 is fine.
3. **Length tolerance**: ±1 mm is acceptable.
4. **Surface**: mill finish OK; clear anodise preferred (adds ~₹60–100
   per 600 mm length).
5. **Slot dimensions**: if the profile is a "slot" type (with internal
   channel), confirm the interior is at least ~14 mm in the 20 mm direction
   so the driver strip fits (standard 80×20 slot profiles are ~76 × 16 mm).
