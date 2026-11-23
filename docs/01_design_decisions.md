# Design Decisions — Why Each Component Was Chosen

> Every significant design choice in V0, with the engineering rationale.

---

## 1. Driver Topology

**Decision**: AL8860 constant-current buck, 7 separate drivers (one per LED string).

**Why**:
- LEDs are current-driven, not voltage-driven
- Buck topology is most efficient (vs linear which dissipates heat)
- 24 V input > max LED Vf (17.55 V for white) so buck works
- One driver per string prevents current imbalance
- Different LED types (white/red/blue/DR) need different currents — cannot share

**Alternatives rejected**:
- LM317 linear: Dissipates 6 W, needs heatsink on driver
- Resistor in series: Not constant current, drifts with temperature
- Boost converter: Not needed (24 V already > Vf)
- SEPIC/flyback: Overkill, too complex

---

## 2. Number of Drivers

**Decision**: 7 drivers (4W + 1R + 1B + 1DR).

**Why**:
- Parallel LED strings need per-string current regulation (current steals)
- Different LED types have different Vf and current needs
- Mixing 3-LED and 4-LED strings in same driver doesn't work

**Why 4 white drivers (not 1)**:
- 1 driver could not run 12 LEDs in series (need 70 V input)
- 1 driver with 4 parallel strings would have current imbalance
- 4 drivers with 1 string each is balanced and simple

---

## 3. PWM Frequency — 2 kHz (NOT 400 Hz)

**Decision**: 2 kHz PWM dimming.

**Why**:
- Fish detect flicker up to 100-200 Hz (some species higher)
- 400 Hz is technically above most fish detection but causes photo banding
- 2 kHz is well above all biological flicker detection
- AL8860 supports up to 20 kHz — 10× headroom

**Trade-off**: Higher PWM frequency = slightly more switching loss. At 2 kHz this is negligible (< 0.1% efficiency loss).

---

## 4. ESP32 Interface — Direct GPIO (NO 2N7002)

**Decision**: ESP32 GPIO → 1 kΩ series → AL8860 CTRL. 100 kΩ pull-down to GND. No MOSFET.

**Why**:
- AL8860 CTRL is high-impedance analog/PWM input
- 3.3 V ESP32 GPIO > 2.5 V CTRL logic-high threshold
- 2N7002 adds cost, complexity, and a failure mode for zero benefit

**Why 1 kΩ series**:
- Limits inrush if GPIO mis-configured
- Limits current during fast PWM edges (reduces EMI)

**Why 100 kΩ pull-down**:
- Keeps LEDs OFF during ESP32 boot
- ESP32 GPIO defaults to input (high-Z) at boot — without pull-down, CTRL would float and LEDs could flash

---

## 5. Schottky Diode — SS3100 (NOT SS24)

**Decision**: SS3100 (100 V / 3 A).

**Why**:
- In buck on 24 V, diode reverse voltage = V_IN + V_F_LED
- For white string: 24 + 17.55 = 41.55 V — already over SS24's 40 V rating
- 100 V rating gives 60 V safety margin
- 3 A current rating handles 0.303 A blue with 10× margin

**Why not use SS24 anyway**:
- 40 V rating is technically within operating range but no margin for transients
- Inductive spikes at LX during switch turn-off can add 5-10 V
- Failure mode is catastrophic (diode short → AL8860 destroyed)

---

## 6. Input Capacitor — 22 µF 1210 (NOT 10 µF 0805)

**Decision**: 22 µF / 50 V X7R in 1210 case (Murata GRM32ER71H226KE15L).

**Why**:
- Ceramic capacitors lose capacitance at DC bias (DC-bias derating)
- 10 µF 0805 measures ~4-5 µF at 24 V DC (more than 50% loss)
- 22 µF 1210 measures ~18-20 µF at 24 V (only 10% loss)
- Adequate input capacitance for AL8860's discontinuous input current

**Why this is important**:
- Insufficient input capacitance causes:
  - Input voltage ripple (could trigger UVLO on AL8860)
  - Voltage stress on AL8860 internal switch
  - EMI from pulsed current draw

---

## 7. Inductor — Würth 7447783680 (68 µH)

**Decision**: 68 µH shielded, 0.95 A saturation.

**Why 68 µH**:
- AL8860 typical application uses 33-100 µH
- 68 µH gives good balance of ripple current and size
- At 200 kHz switching, 68 µH limits ripple to ~30% of DC current

**Why shielded**:
- Reduces radiated EMI (important for aquarium with sensitive electronics)
- No magnetic coupling between drivers (if placed close)

**Why 0.95 A saturation**:
- 0.303 A max (blue string) × 1.3 (ripple) = 0.4 A peak
- 0.95 A Isat gives 2.4× margin

---

## 8. Current Sense Resistor — Vishay WSL2512

**Decision**: WSL2512 1% 1W (4-terminal sense resistor).

**Why 1% tolerance**:
- 5% tolerance = ±12% current error
- 1% tolerance = ±2.5% current error
- For predictable, repeatable LED brightness, 1% is mandatory

**Why 2512 size**:
- Large enough to dissipate 30 mW with negligible self-heating
- Small enough to fit in tight layout
- 1 W power rating is overkill but gives thermal margin

**Why 4-terminal (Kelvin)**:
- Lower sensing error at high currents
- More accurate current regulation

**Why not standard 0805/1206**:
- 0805: 0.125 W, marginal thermal
- 1206: 0.25 W, OK but harder to hand-solder precisely

---

## 9. Bulk Input Capacitor — 220 µF / 50 V Electrolytic

**Decision**: Nichicon UPW1H221MPD (220 µF / 50 V, low ESR, 105 °C).

**Why 220 µF**:
- PSU can have output ripple at full load
- 220 µF provides low-impedance source for AL8860 inputs
- Reduces input voltage droop during transient load changes

**Why 50 V**:
- 35 V would only be 11 V above 24 V (no surge margin)
- 50 V gives 26 V margin for transients
- Same cost, better safety

**Why Nichicon UPW series**:
- Low ESR (good for switching supply input)
- 105 °C rated (long life)
- 5,000-7,000 hour lifetime at full load

---

## 10. Fuse — 2A Slow-Blow

**Decision**: Littelfuse 0215002.MXP (2A / 250V slow-blow, 5×20mm).

**Why 2A**:
- Maximum continuous current: ~0.92 A
- 2× margin for sustained overcurrent
- Catches gross faults (PSU failure, PCB short)

**Why slow-blow**:
- Inrush current at PSU turn-on: 2-3 A for ~50 ms
- Fast-blow would nuisance-trip on every power-on
- Slow-blow (T) handles inrush but trips on sustained overcurrent

---

## 11. PSU — Mean Well LRS-35-24 (External)

**Decision**: Mean Well LRS-35-24 (24 V / 1.5 A / 36 W) mounted external to light.

**Why external PSU**:
- Safety: No mains voltage inside the aquarium light
- Easier certification (PSU is already certified)
- Heat from PSU does not enter the light housing
- User can replace PSU without opening light

**Why 36 W rating**:
- 22 W typical load, 25 W peak
- 1.5 A vs 0.92 A typical — 60% margin
- Allows future expansion (more LEDs, longer length)

**Why Mean Well LRS**:
- Reputable brand, 3-year warranty
- UL/CE/CCC certified
- Available in India via Sunrom, Evelta
- Reasonable cost (~₹450 in India)

---

## 12. Controller — ESP32-C3 SuperMini

**Decision**: ESP32-C3 SuperMini (RISC-V, Wi-Fi, BLE, USB-C).

**Why ESP32-C3**:
- Cheap (~₹250)
- USB-C native (no extra programmer needed)
- Wi-Fi + BLE for future app control
- Enough GPIO for 4 PWM channels
- 3.3 V logic compatible with AL8860 CTRL

**Why not ESP32-S3**:
- Overkill, more expensive, more power
- C3 is sufficient for V0 control needs

**Why SuperMini form factor**:
- Small (similar to Arduino Nano)
- USB-C for easy programming
- Onboard 3.3 V regulator
- Available on Robu/Amazon IN

---

## 13. ESP32 Power — 24V → 5V Isolated DC-DC + 3.3V LDO

**Decision**: Mean Well IRM-02-5 (24V → 5V isolated) + AMS1117-3.3 (5V → 3.3V).

**Why isolated**:
- Galvanic isolation between 24V LED rail and ESP32
- Protects ESP32 from driver section faults
- Required for safety if user touches ESP32 + light frame

**Why 2-step (24V → 5V → 3.3V)**:
- Linear regulator from 24V → 3.3V would dissipate (24-3.3) × 0.2A = 4.1W (too much)
- IRM-02-5 is 80% efficient, dissipates only 0.5W
- AMS1117-3.3 from 5V dissipates only 0.34W (acceptable)

**Why not use USB-C charger**:
- Adds another wall adapter
- More clutter
- But it IS an acceptable alternative for V0

---

## 14. Thermal Architecture — MCPCB + Aluminium Extrusion

**Decision**: LED → aluminium MCPCB → thermal pad → 6063 aluminium extrusion.

**Why MCPCB (not FR4)**:
- FR4 thermal conductivity: 0.3 W/mK
- Aluminium MCPCB: 1-2 W/mK
- 5-7× better heat spreading
- Without MCPCB, LEDs would overheat at 250 mA

**Why 6063 aluminium extrusion (not 6061)**:
- 6063 has slightly better thermal conductivity (200 vs 165 W/mK)
- Easier to extrude into complex profiles
- Cheaper for custom shapes
- 6063-T5 is the most common aquarium light profile

**Why passive cooling (no fan)**:
- Fans fail (MTBF ~30,000 hours)
- Fans introduce noise
- Fans allow dust ingress
- 22W is manageable with adequate extrusion

**Why thermal interface material**:
- Eliminates air gap between MCPCB and extrusion
- Air gap = 0.025 W/mK (insulator!)
- Thermal pad (3 W/mK) = 100× better heat transfer

---

## 15. Diffuser — Opal Acrylic 3mm

**Decision**: Opal (white translucent) cast acrylic, 3mm thickness.

**Why opal (not clear)**:
- Hides individual LED hotspots
- Provides even illumination
- Better aesthetic
- Trade-off: ~30% light loss vs clear

**Why acrylic (not glass or polycarbonate)**:
- Cheaper than glass
- Lighter than glass
- Won't shatter like glass near water
- Polycarbonate yellows over time

**Why 3mm**:
- Rigid enough to span 60cm with simple supports
- Thin enough to not block too much light
- Standard thickness (cheap)

**Why cast (not extruded)**:
- Better optical quality
- No internal stress (won't crack)
- More consistent colour

---

## 16. Mounting — Adjustable Bracket

**Decision**: Stainless steel adjustable rim bracket.

**Why adjustable**:
- Aquarium rim widths vary (10-25mm typical)
- Light should sit close to water for good reflection
- Should be able to tilt for glare control

**Why stainless**:
- Won't rust in humid aquarium environment
- Strong enough for light weight (~1 kg)
- Standard aquarium mounting hardware

---

## 17. NO 2N7002 MOSFET

**Original design had**: ESP32 → 2N7002 → AL8860 CTRL

**Corrected to**: ESP32 GPIO → 1 kΩ → AL8860 CTRL directly.

**Why removed**:
- AL8860 CTRL is high-impedance analog input
- 3.3V ESP32 GPIO > 2.5V logic-high threshold
- 2N7002 adds cost (₹20-40) and a failure mode
- One less BOM line = simpler assembly

**When you WOULD need 2N7002**:
- If ESP32 was 5V logic and AL8860 CTRL was 3.3V max (but CTRL is 6V tolerant)
- If you needed level shifting for some reason
- For high-side switching (not needed here)

---

## 18. NO Mains Voltage Inside Light

**Decision**: 24V external PSU, no mains in light housing.

**Why**:
- Safety: User never touches mains voltage
- Easier certification (PSU is pre-certified)
- Reduced EMI/EMC compliance burden
- IP rating easier (no mains connector)

**Trade-off**:
- External PSU block on floor or behind tank
- DC cable visible
- PSU brick needs to be water-resistant location

---

## 19. Open-LED and Short-LED Protection

**Decision**: Rely on AL8860 built-in OVP/OCP. No external protection.

**Why**:
- AL8860 has built-in over-voltage protection (auto-latch)
- AL8860 has built-in over-current protection
- LED failures are rare and the protection handles them
- Adding fuses per LED string adds cost and complexity

**Failure mode analysis**:
- LED fails open: String current stops, OVP triggers, channel shuts down. Other channels OK.
- LED fails short: Vf drops, AL8860 regulates at lower voltage, no safety issue.
- Driver IC fails: Fuse on 24V bus blows, all LEDs off. Safe.

---

## 20. No Bluetooth/Wi-Fi in V0 Firmware

**Decision**: V0 uses USB serial only. BT/Wi-Fi deferred to V1.

**Why**:
- V0 is for engineering validation
- Serial control via USB is sufficient for bench testing
- App development is a separate project
- Reduces V0 complexity and bug surface

**V1 plan**:
- Add BLE control via phone app
- Pre-defined profiles (sunrise, sunset, weather, presets)
- Wi-Fi for OTA firmware updates

---

## 21. MCPCB / LED Arrangement — "4 Uniform Boards" (Chosen 2026-09-01)

**Decision**: 4 MCPCBs of identical geometry (140 × 20 mm, 5 LEDs each),
laid end-to-end along the 600 mm extrusion at a continuous 28 mm pitch.
Two population designs: boards 1–2 carry the blue pair, boards 3–4 the
deep-red pair; the red string runs serially across all 4 boards (12 white
+ 4 red + 2 blue + 2 deep-red = 20 LEDs). Full spec in
`extrusion_dims.md` §3; connector wiring in `pcb_layout_notes.md` §3.2.

**Why**:
- Every channel is evenly distributed → uniform colour wash along the
  whole bar. Even distribution is the product premise (fish-colour
  enhancement), and the opal diffuser can't fully hide a clustered red
  block.
- 2 board designs × 4 is the cheapest fab split (JLCPCB panels by
  design, not by board).
- Keeps the audited 7-driver architecture and every RSET/current
  unchanged — no electrical rework.
- Colour series chains (red ×4, blue ×2, deep-red ×2) are completed with
  short traces on the driver PCB between J2–J5, so the driver board owns
  all joints → clean TP-02 channel isolation.

**Alternatives rejected**:
1. *7 separate strips* (one per string): zero inter-board wiring, but the
   colour channels read as localised blocks through the diffuser and
   4 unique board designs cost more to fabricate and stock.
2. *More drivers* (split colour into 1-LED strings so every board is
   self-contained): would need 12 drivers vs 7 → ≈ +₹600–700 prototype /
   +₹100 production, and rewrites the audited architecture. Deferred to
   V1 as a possible simplification.

**Cost impact (V0)**: MCPCB BOM row unchanged (qty 4 × ₹120 = ₹480);
only the description changes.

**Driver housing — DECIDED (2026-09-01)**: slender strip **≤ 14 mm wide**
in the extrusion cavity (the 80 × 20 profile has ~16 mm interior; a
580 × 50 mm board never fitted). External box and bigger extrusion were
rejected to keep the light a self-contained bar. See
`pcb_layout_notes.md` §1.
