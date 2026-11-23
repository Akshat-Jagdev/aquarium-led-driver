# TP-02 — Full PCB Bench Validation

> **Goal**: validate the populated V0 driver PCB end-to-end on the bench
> (not yet in the aluminium housing) before the mechanical assembly.
> **Phase**: C (full PCB prototype).
> **Time**: ~3 hours.

## 1. Prerequisites

- TP-01 passed on every channel type (white / red / blue / deep-red)
- V0 PCB assembled per `hardware/mechanical/assembly_drawing.md` §3.1
- Visual inspection of the PCB done (no solder bridges, no missing parts)

## 2. Equipment

- 24 V / 1.5 A bench PSU (current limit 1.0 A for safety)
- Multimeter (V, mA)
- Oscilloscope (2 channels minimum)
- 4× known-good LED MCPCBs from TP-01 (or fresh MCPCBs wired up)
- ESP32-C3 SuperMini, programmed
- Photodiode or lux meter (optional but useful for relative measurements)

## 3. Pre-power checks

1. **No 24 V applied yet.** Measure resistance from 24 V bus to GND with
   multimeter on ohms range. Should read > 1 kΩ (bulk cap charging).
   If you read < 10 Ω, **do not power up** — find the short.
2. Verify each AL8860 has its 100 nF within 2 mm of VIN pin.
3. Verify CTRL pins all measure ~100 kΩ to GND through their pull-downs.
4. Verify fuse is installed (or bench PSU current limit set to 1 A).
5. Verify rocker switch is OFF.

## 4. Initial power-up (no LEDs connected)

1. Connect 24 V bench PSU, current limit 1 A.
2. With rocker OFF, measure 24 V across the input pads: 0 V (good).
3. Flip rocker ON. Observe:
   - PSU current: 30–60 mA (just the 220 µF charging + ESP32 idle)
   - 24 V bus: stable at 24.0 V ± 0.2 V
   - 5 V rail (after IRM-02-5): 5.0 V ± 0.1 V
   - 3.3 V rail (after AMS1117): 3.30 V ± 0.05 V
4. Send serial `o` to ESP32 to confirm it responds.

## 5. Channel-by-channel bring-up

**Do this one channel at a time.** For each:

1. Connect one MCPCB to the corresponding header (J2, J3, J4, or J5).
2. Send the profile that activates only that channel.
3. Measure:
   - PSU current increase (should match `power_thermal_calculator.py`
     output for that channel)
   - LED string current (insert DMM in series with the string)
   - LED string voltage
   - LX node waveform on scope (clean square wave, no ringing > 2 V)
4. Confirm the channel responds to PWM (toggle from 0 to full on
   smoothly).

Repeat for all 7 channels.

## 6. Cross-coupling checks

1. Run all channels at full brightness simultaneously (profile `3`).
2. Measure each channel's current: should still be within ±5% of the
   single-channel value. If one channel drops > 10%, the 24 V bus is
   sagging — check bulk cap and trace widths.
3. Scope each CTRL line: should be a clean square wave, no noise > 0.5 V.
4. Listen for any audible whine — should be silent at 2 kHz PWM.

## 7. Thermal sanity check (short version)

1. Run profile `3` for 15 minutes.
2. Touch each AL8860 with a finger (or use IR thermometer):
   - Should be warm, not too-hot-to-touch (< 60 °C).
3. Power down, touch the aluminium extrusion (no MCPCB attached yet).
4. If anything is unexpectedly hot, **stop** and investigate.

## 8. Pass criteria

- [ ] All 7 channels bring up at expected current ±5%
- [ ] All CTRL signals are clean square waves
- [ ] 24 V bus stays within ±0.3 V at full load
- [ ] No audible whine
- [ ] No thermal issues in 15 min
- [ ] ESP32 responds to serial commands reliably

## 9. If anything fails

**Do not** proceed to mechanical assembly until all issues are fixed.
Re-run TP-01 on the failing channel to isolate whether it's a
component-level problem or a PCB-level problem.

## 10. What to record

Capture and save (in `test_procedures/results/TP-02_<date>/`):

- Photos of the populated PCB
- Scope screenshots of each LX node
- Scope screenshots of each CTRL pin
- All current measurements in a table
- Any anomalies or unusual observations

## 11. Next steps after TP-02 passes

- Move to mechanical assembly per `hardware/mechanical/assembly_drawing.md`
- Then run **TP-03 (optical compare profiles A/B/C/D)** with the
  assembled unit
