# Driver Architecture Audit — Aquarium V0

> Full critical review of the proposed AL8860 driver architecture.
> **Conclusion**: 0 show-stoppers. Several medium-severity items corrected before PCB layout.

---

## 1. Summary of Findings

| # | Item | Original | Corrected | Severity |
|---|------|----------|-----------|----------|
| 1 | Driver topology | AL8860 buck per string | SAME | OK |
| 2 | Number of drivers | 7 | SAME | OK |
| 3 | White string config | 4× of 3 LEDs | SAME | OK |
| 4 | Red string config | 1× of 4 LEDs | SAME | OK |
| 5 | Blue string config | 1× of 2 LEDs | SAME | OK |
| 6 | Deep Red config | 1× of 2 LEDs | SAME | OK |
| 7 | RSET calc (white) | 0.40 Ω | SAME | OK |
| 8 | RSET calc (red) | 0.82 Ω | SAME | OK |
| 9 | RSET calc (blue) | 0.33 Ω | SAME | OK |
| 10 | RSET calc (DR) | 0.82 Ω | SAME | OK |
| 11 | ESP32 → AL8860 interface | 2N7002 N-MOSFET | **Direct GPIO + 1 kΩ** | MEDIUM |
| 12 | PWM frequency | 400 Hz | **2 kHz** | MEDIUM |
| 13 | Schottky diode | SS24 (40V/2A) | **SS3100 (100V/3A)** | MEDIUM |
| 14 | Input capacitor | 10 µF/50V X7R | **22 µF/50V X7R 1210** | MEDIUM |
| 15 | Inductor | Würth 7447783680 | SAME | OK |
| 16 | Bulk input cap | 100–220 µF/35V | **220 µF/50V** | LOW |
| 17 | Fuse | 2A | SAME | OK |
| 18 | Power budget | ~20–25W | ~22W | OK |
| 19 | PSU | LRS-35-24 | SAME | OK |
| 20 | Thermal path | MCPCB → extrusion | SAME (measure to verify) | LOW (test) |
| 21 | Mains in light | NO | SAME | OK |

---

## 2. Detailed Analysis

### 2.1 Topology — PASS

**AL8860 constant-current buck** is the correct choice:
- LEDs are inherently current-driven devices
- 24 V input comfortably higher than max LED Vf (17.55 V for white string)
- Built-in PWM dimming via CTRL pin
- Built-in OVP, OCP, OTP protection
- 40 V abs max on VIN allows safe 24 V operation
- 1.5 A internal switch handles 0.303 A blue string with 5× margin

**Why not alternative topologies**:
- **Linear regulator** (LM317 etc): Dissipates 6 W as heat, requires heatsink on driver, inefficient
- **Resistor in series**: Not constant current, drifts with temperature, poor efficiency
- **Generic PWM LED module**: No current regulation, LEDs over-driven at low PWM, no protection
- **Boost converter**: Not needed; 24 V > max Vf already
- **SEPIC / flyback**: Overkill for this power level, much more complex

**Conclusion**: AL8860 buck per string is the right call.

### 2.2 Number of Drivers — PASS

**7 drivers** for 7 strings is correct:
- Cannot parallel LEDs without per-string current regulation (current would steal between strings)
- Cannot put different LED types in same string (different Vf)
- Cannot put 3 LEDs and 4 LEDs in same string with same current (one would be wrong brightness)

**Alternative considered**: 4 drivers (one per channel type), with parallel LED strings per channel.
- **Rejected**: Parallel strings of 3 white LEDs would have current imbalance (one string gets 280 mA, another gets 220 mA). This causes uneven brightness and uneven aging.

**Conclusion**: 7 independent drivers is correct.

### 2.3 RSET Calculations — PASS

Formula: `I_LED = 0.1 V / R_SET` (from AL8860 datasheet)

| Channel | Target I | RSET calc | Use | P in RSET | P rating OK? |
|---------|---------|-----------|-----|-----------|--------------|
| White | 250 mA | 0.400 Ω | 0.40 Ω | 25 mW | Yes (1 W rating) |
| Red | 120 mA | 0.833 Ω | 0.82 Ω | 12 mW | Yes |
| Blue | 303 mA | 0.330 Ω | 0.33 Ω | 30 mW | Yes |
| Deep Red | 120 mA | 0.833 Ω | 0.82 Ω | 12 mW | Yes |

All RSET resistors are Vishay WSL2512 1% 1W (or equivalent).
The 1% tolerance is important — 5% would give ±12% current error.

**Conclusion**: RSET values are correct.

### 2.4 ESP32 → AL8860 Interface — MEDIUM ISSUE, CORRECTED

**Original proposal**: ESP32 GPIO → 2N7002 N-MOSFET → AL8860 CTRL

**Problem**:
- 2N7002 is unnecessary. AL8860 CTRL is a high-impedance analog/PWM input that can be driven directly from a 3.3 V GPIO.
- The 2N7002 adds:
  - Extra component cost (₹5-10 × 4 = ₹20-40)
  - Extra failure mode (MOSFET short = CTRL stuck HIGH = lights stuck on)
  - Extra PCB complexity
  - Voltage drop (Vgs(th) ~1 V) which limits how "low" you can pull CTRL

**Corrected**:
```
ESP32 GPIO --[1kΩ]--+---- AL8860 CTRL
                     |
                 [100kΩ]
                     |
                    GND
```

- 1 kΩ series resistor: Limits inrush if GPIO is mis-configured as OUTPUT and shorted to GND/VCC. Also limits current during PWM transition.
- 100 kΩ pull-down: Keeps CTRL low during ESP32 boot, BEFORE firmware takes control. Without this, LEDs could flash on during boot.

**Conclusion**: Remove 2N7002. Use direct GPIO with series resistor and pull-down.

### 2.5 PWM Frequency — MEDIUM ISSUE, CORRECTED

**Original**: 400 Hz

**Problems**:
- Many fish detect flicker up to 100-200 Hz
- Photos/videos of the tank show banding
- Eye strain for the viewer

**Corrected**: **2 kHz**

**Implementation** (ESP32-C3 Arduino):
```cpp
ledcSetup(channel, 2000, 12);  // 2 kHz, 12-bit (0-4095)
ledcAttachPin(GPIO, channel);
ledcWrite(channel, 2048);  // 50% duty
```

**AL8860 PWM capability**: Up to 20 kHz. We have 10× headroom.

**Conclusion**: 400 Hz is wrong, 2 kHz is correct.

### 2.6 Schottky Diode — MEDIUM ISSUE, CORRECTED

**Original**: SS24 (40 V / 2 A)

**Problem**: In a buck on 24 V input, the diode sees:
- Reverse voltage = V_IN + V_F_LED ≈ 24 V + Vf
- For white string: 24 + 17.55 = 41.55 V (already over 40 V rating!)
- Plus inductive spike during switch turn-off (typically +5-10 V)

**SS24 failure mode**: Avalanche breakdown → thermal runaway → diode short → catastrophic failure of AL8860 (LX pin to GND short).

**Corrected**: **SS3100 (100 V / 3 A)**

- Reverse voltage margin: 100 - 41.55 = 58 V (very safe)
- Current margin: 3 A vs 0.303 A peak (10× safe)
- Forward drop: 0.45 V (vs 0.30 V for SS24) — only ~3% efficiency loss
- Same package (SMA), same footprint, same price

**Conclusion**: SS24 is unsafe, SS3100 is correct.

### 2.7 Input Capacitor — MEDIUM ISSUE, CORRECTED

**Original**: 10 µF / 50 V X7R

**Problem**: DC-bias derating of ceramic capacitors.
- A 10 µF / 50 V X7R in 0805 case measures ~4-5 µF at 24 V DC
- AL8860 needs more capacitance at VIN to handle the discontinuous input current of a buck

**Corrected**: **22 µF / 50 V X7R in 1210 case**
- Murata GRM32ER71H226KE15L or equivalent
- DC-bias derating: ~18-20 µF effective at 24 V (still 4× better than 0805)
- Or use 2× 10 µF in 1210 in parallel for further margin

**Additional recommendation**: Add 100 nF X7R 0603 right at each AL8860 VIN pin for high-frequency bypass. (Already in BOM, but emphasize placement near VIN.)

**Conclusion**: Use 22 µF 1210, not 10 µF 0805.

### 2.8 Inductor — PASS

**Würth 7447783680** is appropriate:
- 68 µH at 200 kHz gives good ripple current for AL8860
- 0.95 A saturation handles 0.303 A blue string with 3× margin
- Shielded (WE-PD series) — minimal radiated EMI
- Low DCR (0.30 Ω) — low DC loss

**Verification needed** during prototype: measure ripple current on bench, check actual saturation at operating point.

**Conclusion**: Inductor choice is correct.

### 2.9 Bulk Input Capacitor — LOW PRIORITY

**Original**: 100–220 µF / 35 V electrolytic

**Recommendation**: 220 µF / 50 V (Nichicon UPW1H221MPD) for:
- Better surge margin (35 V is only 11 V above 24 V, 50 V is 26 V above)
- Same cost
- Better temperature rating

**Conclusion**: Use 50 V rating for safety margin.

### 2.10 Fuse — PASS

**2A slow-blow** is correct:
- Maximum PSU current at full load: ~0.92 A
- Inrush current: ~2-3 A for <100 ms at PSU turn-on
- Slow-blow (T) rating handles inrush without nuisance blowing
- 2 A rating trips at ~3-4 A sustained (typical slow-blow curve)

**Conclusion**: Fuse is correct.

### 2.11 Power Budget — PASS

Calculated per channel:

| Channel | String V | String I | P_str | Strings | P_total |
|---------|----------|----------|-------|---------|---------|
| White | 17.55 V | 0.250 A | 4.39 W | 4 | 17.6 W |
| Red | 8.40 V | 0.120 A | 1.01 W | 1 | 1.0 W |
| Blue | 6.32 V | 0.303 A | 1.91 W | 1 | 1.9 W |
| Deep Red | 4.30 V | 0.120 A | 0.52 W | 1 | 0.5 W |
| **TOTAL** | | | | | **21.0 W** |

Plus ~5% driver losses (P_switch + P_diode + gate drive) = **~22 W total**
PSU current at full load: **~0.92 A**
LRS-35-24 rating: 1.5 A → **63% margin**

**Conclusion**: PSU is correctly sized.

### 2.12 Thermal Architecture — TEST REQUIRED

**Heat flow**:
- 21 W into LEDs, 18 W into white LEDs alone
- LUXEON 5050 HE Plus thermal resistance junction-to-case: ~1.5 K/W
- At 250 mA, Vf = 5.85 V → P = 1.46 W per white LED
- ΔT junction-to-case = 1.46 × 1.5 = 2.2 °C (negligible)
- BUT junction-to-ambient depends on MCPCB and extrusion

**Mandatory measurement** (TP-04 in test_procedures):
- LED case (TC) < 85 °C after 2-hour soak
- If > 85 °C → increase extrusion size or reduce white current to 200 mA

**Conclusion**: Thermal path is correct, must be verified by measurement.

---

## 3. Open-LED and Short-LED Behavior

**AL8860 OVP (over-voltage protection)**:
- If LED string opens (e.g., LED fails open), output voltage rises
- AL8860 detects this and latches off the channel
- Other channels continue working
- This is **safe** behavior

**If LED shorts**:
- Vf drops, output voltage drops
- AL8860 regulates at lower voltage, same current
- No safety issue
- Color of that string shifts slightly

**No additional protection needed** for V0.

---

## 4. Final Corrected Architecture

| Item | Value |
|------|-------|
| Driver IC | AL8860W6-7 (×7) |
| Inductor | Würth 7447783680 68 µH (×7) |
| Schottky | SS3100 100V/3A (×7) |
| Input cap | 22 µF/50V X7R 1210 (×7) + 100 nF 0603 (×7) |
| RSET (W/R/B/DR) | 0.40 / 0.82 / 0.33 / 0.82 Ω 2512 |
| Bulk cap | 220 µF/50V electrolytic |
| Fuse | 2A slow-blow |
| ESP32 interface | GPIO → 1 kΩ → CTRL (NO 2N7002) |
| Pull-down | 100 kΩ from CTRL to GND |
| PWM | 2 kHz, 12-bit |
| PSU | Mean Well LRS-35-24 (already owned) |

---

## 5. Pre-PCB Action Items

1. ✅ Order corrected parts (use `bom/lcsc_links.md`)
2. ⏳ Build ONE white channel on perfboard (Phase B)
3. ⏳ Verify bench operation: PSU current, LED Vf, CS pin voltage = 100 mV
4. ⏳ Touch-test: nothing should be hot
5. ⏳ Then start KiCad design

**Do not order the PCB until Phase B is successful.**
