# TP-01 — One-Channel Bench Validation

> **Goal**: validate a single AL8860 channel end-to-end on perfboard before
> committing to a full PCB build.
> **Phase**: B (one-channel prototype).
> **Time**: ~2 hours (first time), ~30 min once you've done it.

## 1. What you're validating

- AL8860 buck topology actually regulates at the design current
- RSET resistor value gives the expected current
- PWM dimming via ESP32 GPIO → 1 kΩ → CTRL works
- No thermal runaway on a single channel
- Schematic text matches reality

## 2. Parts you need

From `bom/BOM_v0_prototype.csv`, plus a few bench extras:

- 1× AL8860W6-7
- 1× Würth 68 µH 7447783680 (or generic 68 µH SMD power inductor)
- 1× SS3100 (or generic 100 V / 3 A Schottky)
- 1× 22 µF/50 V X7R 1210
- 1× 100 nF X7R 0603
- 1× WSL2512 RSET for the channel you're testing:
  - 0.40 Ω for white (250 mA target)
  - 0.82 Ω for red / deep-red (120 mA target)
  - 0.33 Ω for blue (303 mA target)
- 3× LUXEON LEDs of the channel you're testing (1 string)
- 1× 1 kΩ 0603, 1× 100 kΩ 0603
- 1× ESP32-C3 SuperMini, programmed with `pwm_test_sketch.ino`
- 1× Mean Well LRS-35-24 (24 V / 1.5 A)
- 1× small piece of perfboard
- 22 AWG silicone wire, hookup jumpers
- Bench multimeter (with mA range or current clamp)
- Oscilloscope (strongly preferred; minimum: DMM + scope probe)
- 24 V lab PSU **or** current-limited bench supply set to ~0.5 A

## 3. Build the perfboard circuit

Wire the per-channel circuit from `docs/03_schematic_text.md` §3 onto a
piece of perfboard:

```
24V (+) ──┬── 100 nF ──┬── 22 µF ──┬── AL8860 VIN (pin 6)
          │            │           │
          │            │       AL8860 GND (pin 2)
          │            │           │
          │            │           └── AL8860 CTRL (pin 5) ──┐
          │            │                                    │
          │            │                              [100 kΩ]
          │            │                                    │
          │            │                                   GND
          │            │
          │       AL8860 LX (pin 1) ──[68 µH]──┬── LED1 anode
          │                                   │
          │                              [D1 SS3100]
          │                              anode at LX
          │                              cathode at 24V (+)
          │
          GND ── AL8860 CS (pin 4) ──[RSET]── LEDn cathode
```

Keep the switching loop area small — under 50 mm² even on perfboard.
Twist the inductor–diode–AL8860 leads together.

## 4. Pre-power checks

1. **Visual**: no solder bridges, correct polarity on SS3100, all LED
   anodes pointing toward the inductor.
2. **Continuity**: 
   - 24 V bus to AL8860 VIN: < 1 Ω
   - AL8860 GND to 24 V GND: < 1 Ω
   - CTRL pin pulled to GND via 100 kΩ: ~100 kΩ (not open, not short)
3. **No 24 V on CTRL**: with PSU off, confirm CTRL is at 0 V (not
   pulled up by anything).
4. **Fuse**: if you put a fuse in this bench setup, install it; if not,
   use a current-limited PSU set to 0.5 A.

## 5. Power-up sequence

1. Connect bench PSU set to 24 V, current limit **0.5 A**.
2. Connect ESP32 USB to laptop.
3. Apply 24 V.
4. Observe:
   - PSU current draw: should be **< 50 mA** at idle (CTRL pulled low,
     LEDs off).
   - If PSU hits current limit immediately → short, disconnect, find it.
5. Send serial command `o` (all off, default state). Confirm 0 mA on
   the bench ammeter.
6. Send `0` (profile A = white channel at ~85% duty). Confirm:
   - PSU current jumps to expected value (white: ~0.21 A, red: ~0.06 A,
     blue: ~0.11 A, deep-red: ~0.03 A)
   - LEDs light up
   - No audible buzz from inductor

## 6. Measurement checklist

| Measurement | Method | Expected | Pass? |
|-------------|--------|----------|-------|
| LED string current | DMM in series with RSET | 0.25 A (white) / 0.12 A (R/DR) / 0.30 A (B) | ☐ |
| LED string voltage | DMM across LED string | 17.55 V (W) / 8.4 V (R) / 6.32 V (B) / 4.30 V (DR) | ☐ |
| AL8860 VIN | Scope probe | 24 V ± 100 mV ripple | ☐ |
| LX switching waveform | Scope probe | ~200 kHz square wave, 0 → ~24 V | ☐ |
| CTRL voltage | Scope probe | square wave, 0 → 3.3 V at 2 kHz | ☐ |
| Heatsink temp after 5 min | Finger / IR thermometer | < 50 °C | ☐ |

## 7. PWM dimming check

- Send profile `0` (white only at 3500/4095 duty ~85%).
- Send profile `1` (white + red).
- Send `o` (off).
- Visually confirm:
  - Each channel lights up when its duty is non-zero.
  - Each channel goes dark when its duty is 0.
  - No flicker visible at any duty.
  - No audible whine from the inductor (if you hear one, the PWM is
    sub-audible frequency — recheck `PWM_FREQ = 2000`).

## 8. Failure modes and what to do

| Symptom | Likely cause | Action |
|---------|--------------|--------|
| LEDs very dim | RSET value too high | Measure actual current, check RSET spec |
| LEDs full brightness, no dimming | CTRL shorted high or pull-down missing | Check CTRL pin — should be 0 V when ESP32 sends 0 |
| PSU current at limit | Short on output | Disconnect, find short, replace parts if damaged |
| Loud buzz | PWM frequency in 1–10 kHz audible band | Re-check PWM_FREQ = 2000 |
| One LED in string dark | Bad LED solder | Reflow; if still dark, swap LED |
| Heatsink very hot in < 1 min | LED string has wrong current, RSET too low | Power off, check RSET value |

## 9. Pass criteria

- [ ] All 6 measurements in §6 are within expected values
- [ ] PWM dimming works smoothly across full duty range
- [ ] No thermal runaway in 10 min of operation
- [ ] No audible buzz

If all four pass, **TP-02 (full PCB bench)** is next. If anything
fails, fix and re-run before committing to PCB.
