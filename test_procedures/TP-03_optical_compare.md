# TP-03: Optical Comparison & TICA Benchmarking
> Goal: Qualitatively and quantitatively verify that the V0 "Colorboost" spectrum enhances ornamental fish colors better than a standard TICA light.

---

## 1. Test Setup
### 1.1 Equipment
- **The Subject**: COLORBOOST V0 (60cm, Opal diffuser).
- **The Benchmark**: TICA (or equivalent) aquarium LED.
- **The Tank**: 60cm standard tank filled with water (optical properties of water are critical).
- **The Fish**: 1x school of Neon Tetras or Discus (species with high red/blue reflectivity).
- **Camera**: Smartphone with "Pro Mode" (fixed White Balance, fixed ISO, fixed Exposure).

### 1.2 Environmental Control
- **Ambient Light**: Complete darkness in the room (blackout curtains).
- **Positioning**: Mount both lights at the same height (e.g., 5cm above water line).
- **Water**: Use clean, dechlorinated water.

---

## 2. Procedure (The "A/B Test")

### Step 1: Baseline Capture (TICA)
1. Power on the TICA light.
2. Let the fish acclimate for 5 minutes.
3. Take 3 photos:
   - **Top-down**: Direct view of fish.
   - **45-degree**: View of fish from the side.
   - **Wide**: Entire tank glow.
4. **CRITICAL**: Lock the White Balance to "Daylight" or a fixed Kelvin value. Do NOT use "Auto".

### Step 2: Baseline Capture (V0 - Neutral)
1. Turn off TICA; power on COLORBOOST V0.
2. Set V0 to "Neutral" profile (All channels at 50%).
3. Repeat the 3 photos using the exact same camera settings.

### Step 3: The "Colorboost" Test (V0 - Enhanced)
1. Switch V0 to the **Enhanced Profile** (Boost Red and Deep-Red).
2. Take the 3 photos.
3. Observe the "pop" of the red scales/fins of the fish.

---

## 3. Evaluation Metrics

### 3.1 Qualitative Analysis (Visual)
Compare the photos side-by-side:
- **TICA vs V0-Neutral**: Is the light distribution more even? (Check for hotspots).
- **V0-Neutral vs V0-Enhanced**: Do the red colors of the fish look deeper and more saturated?
- **Skin Tone**: Does the blue channel make the water look "natural blue" or "artificial neon"? (Target: Natural).

### 3.2 Quantitative (Optional - if Spectrometer available)
If a spectrometer is available, measure:
- **CRI (Color Rendering Index)**: Target $> 90$.
- **R9 Value**: (Saturated Red). Target: $V0_{R9} > TICA_{R9}$.
- **Peaks**: Verify peaks at 448nm (Blue), 625nm (Red), and 660nm (Deep Red).

---

## 4. Success Criteria
The V0 prototype is considered an optical success if:
1. **Uniformity**: No visible "striping" or hotspots through the opal diffuser.
2. **Color Pop**: Red fish colors are visibly more saturated in "Enhanced" mode than in "Neutral" or "TICA" modes.
3. **No Over-Saturation**: The light does not look "pink" or "purple" to the human eye, but enhances the *fish* specifically.

---

## 5. Reporting
Log results in the project journal:
- [ ] Photos uploaded to project folder.
- [ ] R9 value measured (if applicable).
- [ ] Verdict: **Pass / Fail / Needs Tuning**.
