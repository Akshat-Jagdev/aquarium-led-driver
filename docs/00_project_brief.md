# Project Brief — ORNAMENTAL V0 / COLORBOOST

> Complete specification of the aquarium LED light product being developed.
> Last updated: 2026-08-25

---

## 1. Business Context

**Product**: Affordable, scientifically engineered aquarium LED light focused on **fish-colour enhancement** and natural-looking aquarium illumination.

**Gap in Indian market**: Between cheap generic aquarium lights (low quality, no documentation) and expensive premium brands like Chihiros (planted-tank focus, high price).

**Initial target**: Compete with **TICA Color Up** in the fish-colour enhancement segment, not with planted-light brands.

**Positioning**:
> "Premium fish-colour enhancement and natural-looking aquarium illumination at a much lower price, with reliable electronics, proper thermal engineering, measurable specifications, and repairability."

**Pricing**:
- Target retail: **₹3,000–4,000**
- Long-term manufacturing cost: **₹1,500–2,000** per unit (500–1,000+ volume)

**Manufacturing goal**: Indian-sourced as much as realistically possible.

---

## 2. Target Customer

- Indian aquarium hobbyists (especially keepers of ornamental fish: Arowana, Discus, Goldfish, Guppies, Bettas, Cichlids)
- Aquarium maintenance professionals (multiple tank setups)
- Small commercial fish stores

**Customer pain points** (solved by this product):
- Generic lights either look dull or unnaturally coloured
- Most "RGB" lights make water look red, blue, or purple
- Premium imported lights are expensive
- No local service or repair
- No measurable spectrum / power / efficiency data

---

## 3. Optimization Priorities

In strict order:

1. **Fish colour enhancement** (the primary goal)
2. **Natural-looking aquarium appearance**
3. **Scale reflectivity/sparkle**
4. **Good white-light illumination**
5. **Controlled red/warm colour enhancement**
6. **Controlled blue accent**
7. **Low heat**
8. **High reliability**
9. **Long LED/electronics life**
10. **Low manufacturing cost**
11. **Repairability**
12. **Measurable spectrum and optical performance**

**Explicitly NOT optimized for**:
- PAR / photosynthetic photon flux density (plant growth)
- Maximum brightness
- Full spectrum sunlight simulation
- Deep planted-tank penetration

---

## 4. Target Competitor — TICA Color Up

TICA Color Up and Color Up 2/3 are mid-range aquarium lights focused on making fish look more vibrant and reflective, particularly for ornamental species like Arowana.

**Key feature**: Enhances fish colour **without** making the entire aquarium look unnaturally red, blue, or purple.

**Strategy**: Use TICA as a **benchmark for visual performance**, not as a design to copy. We will:
1. Buy a TICA Color Up
2. Characterize its spectrum with a spectrometer
3. Compare our V0 spectrum against it
4. Optimize our design based on visual testing, not spectrum copying

---

## 5. Product Specification (V0)

### 5.1 Physical
- **Length**: ~60 cm (target platform for V0)
- **Other lengths (V1+)**: 30, 45, 60, 90 cm from same extrusion profile
- **Cross-section**: ~80 × 20 mm aluminium extrusion
- **Cooling**: Passive (no fan)
- **Mounting**: Adjustable aquarium rim brackets
- **Ingress**: V0 is bench prototype (no IP rating). Target V1: IP65

### 5.2 Electrical
- **Input**: 24 V DC (external PSU)
- **Mains voltage**: NEVER inside the light
- **Maximum power**: 22 W typical, 25 W peak
- **PSU**: Mean Well LRS-35-24 (24 V, 1.5 A, 36 W) — already owned
- **Protection**: 2 A slow-blow fuse, AL8860 built-in OVP/OCP

### 5.3 Optical
- **4 independent channels** (individually dimmable via ESP32-C3):
  1. **White**: 5700K, 12× LUXEON 5050 HE Plus
  2. **Red**: 625 nm, 4× LUXEON 2835 Color
  3. **Blue**: 448 nm, 2× LUXEON Rubix
  4. **Deep Red**: 660 nm, 2× LUXEON SunPlus 2835
- **Channel currents**: 250 / 120 / 303 / 120 mA
- **PWM frequency**: 2 kHz (above fish flicker detection)
- **Diffuser**: Opal acrylic 3 mm

### 5.4 Control
- **Controller**: ESP32-C3 SuperMini
- **Interface**: Direct GPIO → 1 kΩ → AL8860 CTRL (no level shifter needed)
- **Future**: Bluetooth/Wi-Fi app, presets, sunrise/sunset (deferred to V1+)

### 5.5 Lifetime
- **Target LED life**: 30,000–50,000 hours (L70)
- **Driver life**: 10+ years at 25 °C ambient
- **Warranty target**: 1 year (V0), 2 years (V1)

---

## 6. LED Selection (Final — already ordered)

### White: 12× LUXEON 5050 HE Plus
- **MPN**: L150-5770500600HH0
- **CCT**: 5700K
- **CRI**: ~70
- **Vf**: 5.85 V typical
- **Test current**: 200 mA (we will use 250 mA — verify thermal)
- **Quantity**: 12 (4 strings × 3 LEDs)
- **Application**: Main illumination, scale reflectivity

### Red: 4× LUXEON 2835 Color
- **MPN**: L128-RED10035000002835
- **Peak wavelength**: 625 nm
- **Vf**: 2.1 V typical
- **Test current**: 120 mA
- **Quantity**: 4 (1 string × 4 LEDs)
- **Application**: Warm colour enhancement, Arowana red

### Blue: 2× LUXEON Rubix
- **MPN**: L1RX-RYL1000000000
- **Peak wavelength**: 448 nm
- **Vf**: 3.16 V typical
- **Test current**: 1000 mA (we will use 300 mA — much under-spec)
- **Quantity**: 2 (1 string × 2 LEDs)
- **Application**: Accent, cool tone, fluorescence on some fish

### Deep Red: 2× LUXEON SunPlus 2835
- **MPN**: L1SP-DRD0002800000
- **Peak wavelength**: 660 nm
- **Vf**: 2.15 V typical
- **Test current**: 120 mA
- **Max current**: 250 mA
- **Quantity**: 2 (1 string × 2 LEDs)
- **Application**: Penetrates water, brings out red fluorescence, plant growth if V1 pivots

---

## 7. Driver Architecture (Final — audited)

**Topology**: 7× AL8860 constant-current buck regulators, one per LED string.

**Rationale**:
- Different LED types have different Vf and current requirements
- Do not mix LED types in same string
- Independent current regulation per string
- Simple PWM dimming via CTRL pin
- Built-in protection (OVP, OCP, OTP)

**Channel map**:
| Channel | LEDs per string | Strings | Current | RSET | AL8860s |
|---------|----------------|---------|---------|------|---------|
| White | 3 | 4 | 250 mA | 0.40 Ω | 4 |
| Red | 4 | 1 | 120 mA | 0.82 Ω | 1 |
| Blue | 2 | 1 | 303 mA | 0.33 Ω | 1 |
| Deep Red | 2 | 1 | 120 mA | 0.82 Ω | 1 |
| **Total** | | **7** | | | **7** |

**PWM interface** (no 2N7002):
- ESP32 GPIO → 1 kΩ series → AL8860 CTRL
- 100 kΩ pull-down to GND at first AL8860 per channel
- Frequency: 2 kHz, 12-bit resolution
- One GPIO controls all 4 white AL8860s in parallel

---

## 8. Power Architecture

**External PSU** → fuse → switch → 24 V bus → 7× AL8860 inputs

**Bulk input cap**: 220 µF / 50 V electrolytic + 100 nF X7R
**Per-driver input cap**: 22 µF / 50 V X7R 1210 + 100 nF X7R 0603
**Per-driver output**: LED string (anode at inductor, cathode through RSET to GND)
**Per-driver freewheel**: SS3100 (100 V / 3 A Schottky)

**ESP32 power**: Mean Well IRM-02-5 (24 V → 5 V isolated) + AMS1117-3.3 (5 V → 3.3 V)

---

## 9. Thermal Architecture

**Heat path**:
```
LED junction
   ↓ (LED package thermal resistance, ~1.5–6 K/W)
MCPCB top (aluminium core)
   ↓ (TIM, 1 K/W typical)
Aluminium extrusion 6063
   ↓ (natural convection)
Ambient
```

**Mandatory thermal verification**:
- 2-hour soak at maximum power
- LED case (TC) < 85 °C
- Extrusion < 70 °C (touch-safe)
- Ambient during test ≤ 30 °C

---

## 10. Product Development Philosophy

This is a real product, not a DIY lamp. We follow:

1. Define measurable target
2. Select LEDs from datasheets
3. Prototype electronics (one channel first)
4. Build optical prototype
5. Measure electrical performance
6. Measure thermal performance
7. Measure spectrum
8. Measure optical distribution
9. Compare against TICA
10. Test fish appearance
11. Optimize spectrum
12. Optimize BOM
13. Build engineering prototype (V0)
14. Build small pilot batch (V1)
15. Validate reliability (V1 soak test)
16. Move toward production (V2)

---

## 11. Commercial Targets

| Stage | Volume | BOM Target | Retail | Margin |
|-------|--------|-----------|--------|--------|
| V0 prototype | 1–3 | — | — | R&D cost |
| V1 pilot | 50–100 | ₹2,500 | ₹3,500 | 29% |
| V2 production | 500 | ₹2,000 | ₹3,500 | 43% |
| V3 scaled | 1,000+ | ₹1,500 | ₹3,500 | 57% |

---

## 12. Timeline (V0 to V1)

| Week | Milestone |
|------|-----------|
| 1 | Order parts, install tools |
| 2 | Build and validate ONE AL8860 channel on perfboard |
| 3 | KiCad schematic capture, PCB layout |
| 4 | PCB order (JLCPCB, 7 days), assemble V0 |
| 5 | Bench test full V0, optical test profiles A/B/C/D |
| 6 | Thermal test (2-hour soak) |
| 7 | Order TICA Color Up, spectrometer, do comparison |
| 8 | V0 design review, V1 spec frozen |
| 9 | Order V1 PCBs, MCPCBs (10 units) |
| 10 | Assemble V1 pilot (10 units) |
| 11 | Reliability soak (100 hr), user feedback |
| 12 | V1 review, V2 BOM optimization |

---

## 13. Open Questions

- [ ] V0 length: 60 cm or 90 cm?
- [ ] Diffuser: opal or clear? (Recommend opal for V0)
- [x] MCPCB: **DECIDED** — 4 small boards (2 designs × 2, 5-LED each, 140 × 20 mm; see `extrusion_dims.md` §3)
- [ ] Mounting: rim bracket, hanging kit, or both?
- [ ] App development: defer to V1 or include in V0?
- [ ] Spectrometer: buy now (HiPeak AS8030 ~₹12,000) or later?
- [ ] TICA Color Up: buy now (~₹2,500-3,500 in India) or after V0 is working?

---

## 14. Links to Other Documents

- `docs/02_audit_report.md` — full audit of driver architecture
- `docs/03_schematic_text.md` — exact wiring
- `docs/01_design_decisions.md` — why each component was chosen
- `bom/BOM_v0_prototype.csv` — parts list with India sourcing
- `test_procedures/` — how to validate each phase
