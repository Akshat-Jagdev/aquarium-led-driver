# Competitive Landscape — Aquarium V0 / COLORBOOST

> India-relevant competitors in the fish-only aquarium light segment.
> Target: ₹3,000–4,000 retail, fish-colour-enhancement focus.

---

## 1. Direct competitors (same segment — colour-enhancement)

### TICA Color Up / Color Up 2 / Color Up 3
- **Manufacturer**: TICA Aquarium (Taiwan; distributed in India by TICA India).
- **Retail (India, 2026)**: ₹4,500–5,500 for 60 cm.
- **Positioning**: "Arowana colour enhancement." White + dedicated red channel.
- **Strengths**:
  - Established brand, easy to find in aquarium shops
  - Decent build quality, anodised aluminium housing
  - Good dimming and on/off switch
- **Weaknesses**:
  - No published spectrum, no measured data
  - Single-colour-channel design (limited spectrum control)
  - No repair path; no spares
  - PSU is internal (mains inside the housing — V0's deliberate non-feature)
  - Premium pricing vs. function delivered

### Venso / SunGrow "colour" lights
- **Retail (India)**: ₹2,500–3,500.
- **Positioning**: generic "RGB" fish lights.
- **Weaknesses**:
  - Often RGB-only (no white) → tinted water
  - Cheap drivers, no constant-current regulation → LED overdrive / burnout
  - 3–6 month typical lifetime
  - No certifications, no warranty service

### Generic Amazon / Flipkart lights
- **Retail (India)**: ₹800–2,500.
- **Positioning**: budget, no brand.
- **Weaknesses**:
  - No spectrum info, no thermal engineering
  - Capacitor-dropper PSU or undersized switching PSU
  - Mains-voltage exposed on housing
  - Warranty is fictional

---

## 2. Premium adjacent (different segment — planted tanks)

These are NOT direct competitors but buyers sometimes cross-shop.

| Brand | Focus | India retail | Notes |
|-------|-------|--------------|-------|
| Chihiros WRGB / WRGB II | Planted tank | ₹8,000–18,000 | App control, RGB-W, overkill for fish-only |
| Twinstar | Planted tank | ₹10,000–25,000 | Premium brand, mostly soft water look |
| ONF / Flat Nano | Planted/small tanks | ₹6,000–12,000 | App control, premium materials |
| ADA Solar / Aquasky | Planted | ₹15,000–40,000 | Luxury positioning |

**Why we don't compete here**:
- Planted tanks prioritise PAR (photosynthetic photon flux), not fish colour
- Customers here already accept premium pricing
- We do not need RGB-W app control to win in our segment

---

## 3. The gap V0 fills

The market has three clear tiers and a visible gap:

```
| Tier        | Price        | Quality     | Spectrum   | Repair | Example          |
|-------------|--------------|-------------|------------|--------|------------------|
| Bottom      | ₹800–2,500   | Poor        | None       | No     | Amazon generics  |
| MID         | ₹4,500–5,500 | OK          | Single-col.| No     | TICA Color Up    |
| --- GAP --- | ₹2,500–4,000 | ?           | ?          | ?      | (this is V0)     |
| Premium     | ₹8,000+      | High        | RGB-W app  | No     | Chihiros         |
```

**V0's positioning**: premium-adjacent engineering (measured data, repairable, 4-channel spectrum control) at MID-tier price.

---

## 4. Specific advantages over TICA (the benchmark)

1. **Spectrum measurability** — published SPDs per profile; TICA publishes nothing.
2. **4 channels vs ~2** — independent control of red, blue, deep-red, white.
3. **Repairability** — every IC is replaceable; TICA has no service path in India.
4. **External PSU** — safer (no mains in housing); replaceable without opening light.
5. **Documented thermal path** — TP-04 thermal soak test is mandatory; TICA has no public thermal data.
6. **Open firmware** — V1 will add BLE + app; customers can add custom profiles.
7. **Lower price at same quality** — V0 retail target ₹3,500 vs TICA ₹5,000.

---

## 5. Competitive risk matrix

| Risk | Severity | Mitigation |
|------|----------|-----------|
| TICA launches a 4-channel model | M | Move on price + repairability + data |
| Chinese OEM copies V0 design | M | Patent the spectrum tuning? Brand on reliability |
| Chihiros drops a budget line | L | Different segment; planted vs fish-only |
| Local Indian competitor launches | H | First-mover advantage; build community |

---

## 6. Differentiation: what we measure and TICA doesn't

| Metric | V0 (published) | TICA (published) |
|--------|----------------|------------------|
| Spectrum per profile | Yes (CSV in `docs/spectrum/`) | No |
| LED junction temp after soak | Yes (TP-04) | No |
| L70 lifetime estimate | Yes (per channel) | No |
| PSU efficiency under load | Measured | No |
| Repair manual | Yes | No |
| App control (V1) | Yes (planned) | No |

---

## 7. Summary

V0 is positioned to win on the **measurable engineering** axis at a price
10–20% below TICA. The plant-tank premium brands are a different segment
and not head-to-head. The biggest commercial risk is a similar product from
a major Indian electronics brand (Syska, Wipro) — but they have not
entered this niche as of 2026.
