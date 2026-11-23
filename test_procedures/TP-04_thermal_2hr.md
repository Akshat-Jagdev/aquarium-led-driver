# TP-04 — Thermal 2-Hour Soak Test

> **Goal**: confirm steady-state LED junction temperature stays below the
> 85 °C L50 limit and the housing stays touch-safe (< 70 °C) under
> continuous full-power operation.
> **Phase**: D (thermal validation).
> **Time**: ~3 hours total (setup + 2 h soak + teardown).

## 1. Prerequisites

- TP-02 fully passed
- Unit assembled in the aluminium extrusion with MCPCBs and diffuser
- K-type thermocouple + reader (or IR thermometer with 0.1 °C resolution)
- Ambient temperature recorded

## 2. Test setup

1. Place the assembled unit **on a non-conductive, non-flammable
   surface** (cardboard box, plywood, etc.). Do NOT mount on a tank —
   you want worst-case stagnant air cooling.
2. Attach thermocouples:
   - **TC1**: on the LED case of one white LED (use a tiny drop of
     thermal paste to attach)
   - **TC2**: on the centre MCPCB top surface
   - **TC3**: on the aluminium extrusion (mid-length)
   - **TC4**: on the driver PCB near an AL8860
   - **TC5**: ambient (in shade, ~10 cm from the unit)
3. Apply profile `3` (all channels full brightness).
4. Record starting ambient.

## 3. Data logging

- Log all 5 thermocouples every **60 seconds** for **120 minutes**.
- Watch for:
  - LED case (TC1): must plateau **< 85 °C**
  - Extrusion (TC3): must plateau **< 70 °C** (touch-safe)
  - Driver (TC4): must plateau **< 90 °C**
- If anything exceeds its limit, **stop the test** and investigate.

A simple logging script (Python):
```python
import time
# Replace `read_tc(i)` with your thermocouple reader call
while True:
    temps = [read_tc(i) for i in range(5)]
    print(f"{time.strftime('%H:%M:%S')} TC1={temps[0]:.1f} TC2={temps[1]:.1f} "
          f"TC3={temps[2]:.1f} TC4={temps[3]:.1f} amb={temps[4]:.1f}")
    time.sleep(60)
```

## 4. Pass criteria

After 120 minutes of continuous operation:

- [ ] LED case TC1 ≤ **85 °C** (ideally ≤ 75 °C)
- [ ] MCPCB TC2 ≤ **80 °C**
- [ ] Extrusion TC3 ≤ **70 °C**
- [ ] Driver TC4 ≤ **90 °C**
- [ ] All readings have plateaued (Δ over last 30 min < 2 °C)
- [ ] No visible discolouration on the MCPCB or extrusion
- [ ] No unusual smell (epoxy, hot plastic — anything = failure)

## 5. If you exceed limits

| Symptom | Likely cause | Action |
|---------|--------------|--------|
| LED case > 85 °C | Inadequate thermal pad, or wrong RSET (too much current) | Check RSET, replace thermal pad with 5 W/mK grade, raise extrusion height off surface |
| Extrusion > 70 °C | Normal in still air; re-test with airflow | Test in a more ventilated area; if still too hot, add thermal mass to extrusion (longer profile) |
| Driver > 90 °C | Insufficient copper under AL8860, or 24 V bus sagging | Check thermals on PCB, add thermal vias, check input cap |

## 6. Record keeping

Save raw data and a plot of temperatures vs. time to:
`test_procedures/results/TP-04_<date>/`. Filename:
- `TP-04_<date>_temperatures.csv`
- `TP-04_<date>_temperatures_plot.png`

The plot should show all 5 traces over 120 minutes.

## 7. After TP-04

If all pass: feed the measured steady-state TC1 temperature into
`tools/led_lifetime_estimator.py` (replace `Tj_use_C`) for an updated L70
estimate.

Next: **TP-05 (spectrum test)** if you have a spectrometer, otherwise
**TP-06 (fish appearance)** and **TP-07 (reliability soak)** in
parallel.
