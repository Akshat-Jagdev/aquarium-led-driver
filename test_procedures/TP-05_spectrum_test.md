# TP-05 — Spectrum Test (Spectrometer Measurement)

> **Goal**: measure the V0 light's spectral power distribution (SPD) for
> each profile and compare against TICA Color Up (or any reference light).
> **Phase**: D (optical validation).
> **Time**: ~3 hours (plus spectrometer setup).

## 1. Prerequisites

- TP-02 and TP-03 passed
- A spectrometer capable of 380–780 nm measurement with reasonable
  resolution (10 nm or better)
  - **Recommended**: HiPeak AS8030 (~₹12,000 on Amazon IN), UPRtek
    MK350D (premium), or a DIY setup using a diffraction grating + phone
    camera (rough but free)
- Dark room (no daylight)
- Tripod or fixed mount for the spectrometer

## 2. Equipment setup

1. Mount the V0 light on the tank (or test rig with water-filled tank).
2. Mount spectrometer at fixed distance (~30 cm from diffuser centre,
   perpendicular to the diffuser face).
3. Set integration time so peak channel reads ~80% of full scale (avoid
   clipping).
4. Cap the spectrometer, take dark-current reading, store it.

## 3. Measurement procedure

For each profile A → B → C → D:

1. Apply profile via serial.
2. Wait 30 seconds for thermal stabilisation (LED output drifts slightly
   with temperature).
3. Capture spectrum (typically a 1-second integration averages out PWM).
4. Record:
   - Filename: `TP-05_<date>_profile<A-D>_V0.csv`
   - Wavelength column (380–780 nm, 1 or 5 nm steps)
   - Intensity column (relative units, normalised later)
5. Repeat 3 times and average (check for drift).

If measuring TICA Color Up:
6. Replace V0 with TICA, set to its "colour" mode.
7. Repeat measurement at the same geometry.
8. Filename: `TP-05_<date>_tica-color.csv`

## 4. Analysis

Use any plotting tool (matplotlib, Excel) to:

1. Plot all V0 profiles on the same chart (380–780 nm).
2. Plot V0 profile D and TICA on the same chart.
3. Compute:
   - **CCT** (correlated colour temperature) for profile A — should be
     close to 5700 K (the white LED spec)
   - **CRI** (colour rendering index) — typical aquarium lights are
     CRI 70–80; our 5050 HE Plus is ~70
   - **Peak wavelengths** for red, blue, deep-red channels — should
     match LUXEON specs (±10 nm)
   - **Spectral gap** between 480 nm and 600 nm — large gap means
     aquariums look more "cyan + orange" which is the TICA-style
     colour-enhanced look

## 5. Pass criteria

- [ ] Profile A spectrum peaks at ~450 nm and ~550 nm (white LED phosphor
      conversion)
- [ ] Profile A CCT between 5000 K and 6500 K
- [ ] Red channel peaks at 620–630 nm
- [ ] Blue channel peaks at 445–455 nm
- [ ] Deep-red channel peaks at 655–665 nm
- [ ] Profile D has all 4 peaks clearly distinguishable
- [ ] V0 spectrum shape comparable to TICA on the colour-enhancement
      profile (not identical, but visually similar)

## 6. Optional: fish-colour metric

Compute the **fish-colour rendering index** if your spectrometer
software supports it. Compare V0 vs. TICA — the goal is parity, not
dominance.

## 7. What to record

Save raw spectrometer CSV + plot PNG to:
`test_procedures/results/TP-05_<date>/`.

## 8. After TP-05

Use the spectrum data to:
- Update the marketing collateral (claimed CCT, CRI, peak wavelengths)
- Decide if a profile needs adjustment (e.g., blue too strong → reduce
  duty in `pwm_test_sketch.ino`)
- Hand off to marketing for a comparison chart vs TICA

Next: **TP-06 (fish appearance test)** if not already done.
