# Risk Register — Aquarium V0

> Known risks and mitigation strategies.
> Severity: H = High, M = Medium, L = Low
> Likelihood: H = High, M = Medium, L = Low

---

## 1. Electrical Risks

### R-E1: LED overcurrent / overheating
- **Severity**: H (catastrophic LED failure)
- **Likelihood**: L (well-designed current limit)
- **Mitigation**:
  - Verified RSET calculations (see `docs/02_audit_report.md`)
  - Use 1% tolerance sense resistors
  - Bench-test each channel before connecting LED string
  - Measure PSU current matches calculated 0.92 A at full load
  - 2-hour thermal soak test (TP-04)

### R-E2: AL8860 OVP latch-up
- **Severity**: M (single channel stuck off)
- **Likelihood**: L (only on LED open failure)
- **Mitigation**:
  - Document OVP behavior in user manual
  - Provide reset procedure (power cycle)
  - Accept as designed behavior

### R-E3: PSU failure
- **Severity**: M (light goes off)
- **Likelihood**: L (Mean Well reliability)
- **Mitigation**:
  - Use Mean Well (3-year warranty)
  - 60% current margin
  - External PSU = user-replaceable
  - V1: Add status LED visible to user

### R-E4: Water ingress to light
- **Severity**: H (electrical hazard, LED damage)
- **Likelihood**: M (V0 has no IP rating)
- **Mitigation**:
  - V0: Bench prototype, NOT for aquarium use yet
  - V1: Target IP65 with sealed end caps
  - V1: Use IP67-rated DC barrel jack
  - User education: "Do not submerge or splash V0"

### R-E5: Wrong polarity LED installation
- **Severity**: M (LED dead, possibly driver damage)
- **Likelihood**: M (assembly mistake)
- **Mitigation**:
  - Clear polarity marking on PCB silkscreen
  - Visual inspection during assembly
  - Add diode reverse-polarity protection on each LED string (V1)

### R-E6: Electrostatic discharge (ESD) to LED
- **Severity**: M (LED degradation over time)
- **Likelihood**: L (LEDs are reasonably ESD-resistant)
- **Mitigation**:
  - Wrist strap during assembly
  - Conductive foam for LED storage
  - V1: Add TVS diodes on LED strings

---

## 2. Thermal Risks

### R-T1: LED junction temperature exceeds 85 °C
- **Severity**: H (drastically reduced LED lifetime)
- **Likelihood**: M (depends on extrusion size)
- **Mitigation**:
  - MANDATORY 2-hour thermal soak test (TP-04)
  - If TC > 85 °C: increase extrusion size, reduce current, or improve TIM
  - Spare white LEDs ordered to allow driver re-tuning
  - Use thermal simulation (FreeCAD + Elmer) before V1

### R-T2: Heatsink too hot to touch
- **Severity**: M (user safety)
- **Likelihood**: M
- **Mitigation**:
  - Limit extrusion surface temp to < 60 °C
  - Mounting bracket design ensures user touches bracket, not extrusion
  - Warning label for V0: "Heatsink may be hot during operation"

### R-T3: Driver IC overheating
- **Severity**: L (AL8860 has internal OTP)
- **Likelihood**: L (dissipation < 150 mW per IC)
- **Mitigation**:
  - Calculate dissipation per channel (30-120 mW)
  - AL8860 thermal resistance junction-to-ambient: ~150 K/W
  - ΔT at 150 mW: 22 K, well within operating range

---

## 3. Optical Risks

### R-O1: Spectrum doesn't match target
- **Severity**: M (product doesn't meet goal)
- **Likelihood**: M (LED ratios are guess)
- **Mitigation**:
  - Buy spectrometer before V1 (HiPeak AS8030 ~₹12,000)
  - Test 4 profiles (A/B/C/D) and document spectrum
  - Compare against TICA Color Up
  - V1: Adjust LED ratios based on results

### R-O2: Fish don't look better than TICA
- **Severity**: H (product fails primary goal)
- **Likelihood**: M
- **Mitigation**:
  - Buy TICA Color Up for side-by-side test
  - Test on multiple ornamental fish species (Arowana, Discus, Guppy)
  - Use controlled environment (same tank, same camera, same settings)
  - Get feedback from aquarium hobbyist community

### R-O3: Aquarium water looks red/blue/purple
- **Severity**: H (visible quality issue)
- **Likelihood**: L (channel ratios designed to avoid this)
- **Mitigation**:
  - Test Profile A (white only) first — should look natural
  - Add red and blue incrementally
  - Document ratios that cause discoloration
  - Default preset avoids "purple water" look

### R-O4: LED hotspots visible
- **Severity**: M (poor aesthetic)
- **Likelihood**: M (depends on diffuser)
- **Mitigation**:
  - V0: Use opal diffuser (test 3mm and 5mm thickness)
  - If hotspots still visible: Increase diffuser thickness or distance
  - V1: Add secondary diffuser

### R-O5: Insufficient brightness
- **Severity**: M (poor customer satisfaction)
- **Likelihood**: L (calculated to be adequate)
- **Mitigation**:
  - Calculate luminous flux per channel from LED datasheets
  - Total: ~2000-3000 lumens (estimate, verify with lux meter)
  - If insufficient: Increase currents (white to 300 mA, etc.) or add more LEDs
  - Lux meter test at water surface, 30 cm depth

---

## 4. Mechanical Risks

### R-M1: Extrusion does not dissipate enough heat
- **Severity**: H (forces redesign)
- **Likelihood**: M
- **Mitigation**:
  - Test on perfboard/extrusion early (before PCB)
  - 2-hour thermal test in TP-04
  - Have 80x30mm and 80x40mm extrusion profiles as backup

### R-M2: Mounting bracket inadequate
- **Severity**: M (light falls into tank)
- **Likelihood**: L (brackets are standard)
- **Mitigation**:
  - Use stainless steel brackets rated for 5+ kg
  - Test on actual aquarium rim
  - Provide safety wire as backup
  - User manual: "Use safety wire to prevent fall into tank"

### R-M3: Acrylic diffuser yellows over time
- **Severity**: L (cosmetic)
- **Likelihood**: L (cast acrylic is UV-resistant)
- **Mitigation**:
  - Use cast acrylic (not extruded)
  - V1: Add UV filter
  - Specify UV-resistant brand (e.g., Plexiglas)

### R-M4: End caps not water-resistant
- **Severity**: M (water ingress)
- **Likelihood**: M (V0 has poor sealing)
- **Mitigation**:
  - V0: Use 3D printed end caps with silicone gasket
  - V1: CNC aluminium end caps with EPDM gasket
  - V1: Target IP65

---

## 5. Firmware/Software Risks

### R-F1: ESP32 firmware bug causes LED to stay on
- **Severity**: M (heat, LED degradation)
- **Likelihood**: L (firmware is simple)
- **Mitigation**:
  - Watchdog timer in firmware
  - Maximum brightness limit in software
  - Hardware: 100kΩ pull-down on CTRL ensures default OFF

### R-F2: PWM signal noise
- **Severity**: L (flicker)
- **Likelihood**: L (ESP32 PWM is clean)
- **Mitigation**:
  - 1 kΩ series resistor filters edge noise
  - 100 nF cap on CTRL pin (optional, for extra filtering)
  - Test with oscilloscope

### R-F3: ESP32 brownout during PWM
- **Severity**: L (LED flicker)
- **Likelihood**: L (USB-powered or regulated)
- **Mitigation**:
  - Use stable 3.3V from AMS1117
  - Add 10 µF + 100 nF near ESP32 power pins
  - Brownout detector enabled in firmware

---

## 6. Business/Commercial Risks

### R-B1: BOM cost exceeds target
- **Severity**: H (commercial failure)
- **Likelihood**: M (initial cost is ~₹4,000, target ₹2,000)
- **Mitigation**:
  - Volume pricing negotiated with suppliers
  - Use Indian suppliers where possible
  - V2: Move to Indian MCPCB fab
  - Run `bom_cost_calculator.py` after every price change

### R-B2: TICA Color Up cheaper than expected
- **Severity**: M (price advantage lost)
- **Likelihood**: L (TICA retail is ~₹4,500-5,500 in India)
- **Mitigation**:
  - Monitor TICA pricing
  - Emphasize reliability, repairability, measurability (not just price)
  - V1: Add features (BLE, app) TICA doesn't have

### R-B3: Component obsolescence
- **Severity**: M (redesign needed)
- **Likelihood**: L (AL8860, LUXEON 5050 are mature products)
- **Mitigation**:
  - Use multiple-source components (Wurth/Bourns inductor, etc.)
  - Subscribe to distributor notifications
  - Have approved alternates documented

### R-B4: Slow time-to-market
- **Severity**: M (competitors move first)
- **Likelihood**: M (V0 is 12 weeks)
- **Mitigation**:
  - Phased release: V0 (engineering), V1 (pilot), V2 (production)
  - V0 is for learning, not for sale
  - V1 can be sold as "developer edition" to early adopters

### R-B5: Certification cost (BIS, CE-equivalent)
- **Severity**: M (₹50,000-100,000 for India BIS)
- **Likelihood**: M (required for V1 sales)
- **Mitigation**:
  - V0: Skip certification, "engineering sample"
  - V1: Budget for BIS registration
  - Use pre-certified PSU (already BIS-registered)
  - Defer to V2 if necessary

---

## 7. Manufacturing Risks

### R-P1: PCBA quality issues
- **Severity**: H (field failures)
- **Likelihood**: L (JLCPCB quality is good)
- **Mitigation**:
  - Visual inspection of every board
  - First 5 boards: 100% bench test
  - 100 boards: 10% bench test
  - 1000+ boards: AOI + 5% bench test

### R-P2: LED binning variation
- **Severity**: M (different colour between units)
- **Likelihood**: L (Lumileds has tight binning)
- **Mitigation**:
  - Order all LEDs in single batch for V0-V2
  - Document bin codes
  - Future: Active binning/sorting if needed

### R-P3: Component sourcing delays
- **Severity**: M (production delay)
- **Likelihood**: M (global chip shortages)
- **Mitigation**:
  - Maintain 3-month inventory buffer
  - Approved alternates for critical parts
  - Multiple suppliers per component

---

## 8. Open Risks Requiring More Data

These cannot be assessed until testing is done:

- **Actual LED spectrum vs expected**: Need spectrometer
- **Actual heatsink temperature**: Need 2-hour soak
- **Fish appearance vs TICA**: Need TICA unit
- **Real-world PSU efficiency under load**: Need measurement
- **LED lifetime at operating current**: Need accelerated life test (or trust Lumileds datasheet)

---

## 9. Risk Summary

| Severity | Count | Action |
|----------|-------|--------|
| High | 5 | Test in V0 phase, mitigate in V1 |
| Medium | 12 | Design in V0, verify in V1 |
| Low | 10 | Document, monitor |

**Overall**: Project is technically sound. Main risks are around optical performance (R-O1, R-O2) which can only be validated by testing. Build V0 → test → iterate.
