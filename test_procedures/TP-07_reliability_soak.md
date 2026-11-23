# TP-07 — Reliability Soak (100-Hour Endurance Test)

> **Goal**: prove the V0 unit can run continuously for 100 hours at full
> power without failure, drift, or thermal runaway. This is the gate to
> declaring V0 ready for V1 pilot production.
> **Phase**: D (final validation gate).
> **Time**: 100 hours unattended + ~1 hour for setup and teardown.

## 1. Prerequisites

- TP-02, TP-03, TP-04 all passed
- Spare fuse, spare AL8860, spare LEDs on hand (in case of failure)
- Power outlet with surge protector
- A way to monitor from another room (camera pointed at the light, or a
  smart-plug reporting current draw)

## 2. Setup

1. Place the unit on a non-conductive surface in a safe location (not
   above the tank — in case of water leak from a hose).
2. Connect the Mean Well LRS-35-24 PSU.
3. Plug the PSU into a **smart plug** that logs power consumption
   (₹1,000–2,000 on Amazon IN; e.g., Tapo P110, Wipro 16A).
4. Apply profile `3` (all channels full brightness).
5. Note the starting current draw on the smart plug app — should be
   ~0.6–0.9 A at 24 V (≈ 15–22 W). Anything outside this range is a
   fault.
6. Set up a phone camera or webcam to take a time-lapse every 30
   minutes (optional but useful for post-mortem).

## 3. Monitoring

You don't need to babysit it, but check:

| Interval | What to check |
|----------|---------------|
| Every 4 hours | Smart-plug current draw (should be steady within ±5%) |
| Every 12 hours | Visual inspection — any discolouration, smell, smoke |
| At 24 hours | Quick functional check — toggle profile, confirm normal operation |
| At 50 hours | Mid-test thermal check (TC1 should still be < 85 °C) |
| At 100 hours | Final measurement and teardown |

## 4. Failure response

If the smart plug shows current dropping to 0 A, or you smell anything,
or the time-lapse shows a visible change:

1. **Unplug immediately.**
2. Inspect for the failed component (look for burnt parts, discoloured
   PCB).
3. Replace the failed part.
4. Document the failure mode in `test_procedures/results/TP-07_<date>/failure_<hour>h.md`.
5. **Reset the clock** — restart the 100-hour count from zero. A unit
   that fails at hour 30 has not passed TP-07.

## 5. Teardown measurements (at hour 100)

1. Power off, measure LED case temperature within 60 seconds of
   shutdown (should still be near steady state).
2. Measure each channel's current (DMM in series) — should be within
   ±5% of starting value. Significant drop indicates LED degradation.
3. Measure the 24 V bus — should be clean, no droop.
4. Visual inspection:
   - PCB solder joints (look for cracks, dullness)
   - LED phosphor (any yellowing?)
   - Wire insulation (any discolouration near hot parts?)
   - End cap / diffuser (any warping?)

## 6. Pass criteria

- [ ] 100 hours of continuous operation completed
- [ ] Current draw remained within ±5% of starting value
- [ ] No component failures
- [ ] LED case temperature at hour 100 ≤ 85 °C
- [ ] Channel currents at hour 100 within ±5% of hour-0 values
- [ ] No visible degradation on visual inspection

## 7. Record keeping

Save to `test_procedures/results/TP-07_<date>/`:
- Smart-plug power log (CSV export)
- Time-lapse frames (optional)
- Failure log (if any)
- Hour-100 measurement sheet

## 8. After TP-07

If passed:
- V0 design is **locked**.
- You can confidently move to V1 pilot (10 units).
- Update README §6 to mark V0 design complete.
- Update `tools/led_lifetime_estimator.py` with measured hour-100
  channel currents for an empirical lifetime estimate.

If failed:
- Diagnose, fix, re-run TP-07 from scratch.
- Common failure modes:
  - Electrolytic capacitor drying out (use 105 °C rated, like Nichicon
    UPW)
  - Solder joint crack from thermal cycling (reflow with leaded solder
    for prototyping)
  - LED wire insulation melting (use higher-temp silicone wire)
  - Connector oxidation (use gold-plated headers)
