# Simulation Report — Aquarium V0 LED channels (Sep 16, 2026)

Script: `sim_v0_channels.py` (hysteretic-buck transient, 2 ns step, stats after 50 µs settle).

## Assumptions
- AL8860 SET reference 100 mV, hysteretic band ±10% of I_set (datasheet-exact band not modeled; tON and fsw scale with this band, average current does not).
- RDS(on) 0.35 Ω, SS3100 Vf 0.5 V, L DCR 0.15 Ω, LED string dynamic R 2 Ω.
- Vf: white string 17.55 V (3×5.85), red 8.0 V (4×2.0), blue 6.4 V (2×3.2), deep-red 4.4 V (2×2.2).
- Switching losses (gate/Coss) not modeled; real η ~1-3 % lower.
- U8/U9 unpopulated (V0), ESP32 USB-powered — excluded.

## Results
channel        I_led(mA) rip(pp) fsw(kHz) duty  tON(ns) Pin(W/ch) eta
White (U1-U4)    249.9   50.7    1276    0.765   600     4.59   0.98
Red   (U5)       122.0   24.6    1532    0.711   464     1.04   0.97
Blue  (U6)       303.1   60.9     708    0.618   872     2.25   0.95
DeepR (U7)       122.0   24.6    1240    0.423   341     0.62   0.92

Power system: 12 V rail load 3.9 W (0.33 A — LM2596 loafing). 24 V rail total 22.6 W / 0.94 A
from LRS-35-24 → 13.4 W headroom of 36 W. Fuse F1 2 A > 0.94 A OK.

## Findings
1. WHITE OVERDRIVE ⚠ — RSET 0.40 Ω sets 250 mA/string but BOM rates white LEDs 200 mA
   (L150-5770500600HH0). 25 % over spec unless datasheet abs-max allows. Options:
   RSET 0.47 Ω → 213 mA, or 0.50 Ω → 200 mA (WSL2512 series has both).
2. tON margin ⚠ — audit rule was tON ≥ 500 ns. White 600 ns OK, Blue 872 ns OK.
   Red 464 ns and Deep-red 341 ns are under, at the ±10% band assumption. Both scale with
   the real hysteretic band; if the AL8860 band is wider they pass. If bench TP-01 shows
   low current accuracy on these channels, raise L (red: 100 µH → ~680 ns; DR: 220 µH → ~750 ns).
3. fsw 1.2–1.5 MHz on white/red/DR is high (band-dependent); extra EMI/switching loss.
   Same L-increase fix lowers fsw.
4. Efficiency per channel 0.92–0.98 (conduction-only) — no action needed.
5. Rail sizing all healthy: LM2596 at 11 % of 3 A, PSU at 63 % of 36 W.
