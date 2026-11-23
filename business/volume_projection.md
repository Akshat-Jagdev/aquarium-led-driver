# Volume Projection — Aquarium V0 / COLORBOOST

> Per-unit cost and margin model at 1 / 100 / 500 / 1000 unit volumes.
> See `unit_economics.md` for the deeper breakdown.

---

## 1. Headline numbers

| Volume | BOM ₹ per unit | Retail ₹ | D2C margin |
|--------|-----------------|----------|------------|
| 1 (V0 prototype) | 4,300 | n/a (engineering) | n/a |
| 100 (V1 pilot) | 3,300 | 3,500 | 6% |
| 500 (V2) | 2,771 | 3,500 | 21% |
| 1,000 (V3) | 2,340 | 3,500 | 33% |
| 5,000 (V3+) | 1,780 | 3,500 | 49% |

> Updated 2026-09-01: the LUXEON LED set (₹376 / ₹330 / ₹280 per unit at
> qty 500 / 1000 / 5000) is now included in every production BOM — earlier
> tables omitted it entirely. Cross-check: `bom/BOM_v0_production_500.csv`
> uses tighter component pricing → **₹2,542/unit at qty 500**; the planning
> tables here use a slightly padded basis (pre-existing ~₹225 gap).

---

## 2. Volume assumptions

### V0 prototype (1 unit)
- Engineer build, learning phase
- No retail sale
- "Cost" includes prototype MCPCB, hand assembly, bench time
- Output: validated design, test reports, spectrum data

### V1 pilot (10–100 units)
- First units made on the same KiCad PCB
- Sells at cost + ~20% to early-adopter aquarium shops + online D2C
- Output: real-world reliability data (TP-07), customer feedback, brand

### V2 (100–500 units)
- Indian MCPCB fab contracted
- Amazon India launch + aquarium-shop dealer network
- Output: market validation, channel build-out

### V3 (500–2,000 units)
- Larger PCB panel runs, custom extrusion
- First BIS registration (if not already done)
- Output: profitable operation

### V3+ (2,000–10,000 units)
- Fully cost-optimised BOM
- V1 firmware (BLE + app) shipped
- Output: scale business

---

## 3. Where each rupee goes at qty 1000

```
Total per unit: ₹2,340 (incl. LEDs)

  LEDs (LUXEON set, 20 pcs)      ████          ₹330    14.1%
  Power (PSU, DC-DC, fuse)       ██████        ₹480    20.5%
  MCPCB (4 boards)               ████          ₹280    12.0%
  Aluminium extrusion            ███           ₹260    11.1%
  Diffuser + thermal pad         ██            ₹200     8.5%
  ESP32-C3 module                ██            ₹180     7.7%
  Drivers + AL8860 stack         ██            ₹170     7.3%
  Other passives / discretes     █             ₹130     5.6%
  End caps + brackets            █             ₹110     4.7%
  PCB (panelised)                ▌             ₹90      3.8%
  Assembly consumables           ▌             ₹50      2.1%
  Pack + shipping allocation     ▌             ₹50      2.1%
```

**Largest costs are power (₹480) + LEDs (₹330) + MCPCB (₹280) + extrusion
(₹260) ≈ 57% of BOM. LEDs are now the third-largest line and the single
biggest sourcing lever.**

Cost-out priorities for V3+:
1. LED pricing via direct Lumileds distributor negotiation (saves ₹40–90/unit)
2. Replace Mean Well LRS-35-24 with Indian equivalent (saves ₹50–80/unit at scale)
3. Custom extrusion profile (saves ₹80–120/unit at scale)
4. Indian MCPCB fab at 5,000+ (saves ₹30–60/unit)

---

## 4. Selling scenarios at qty 500

| Channel | Mix | Realisation ₹/unit | Margin @ ₹2,771 BOM |
|---------|-----|----------------------|-----------------------|
| Direct D2C (own website) | 30% | 3,500 | 21% |
| Amazon India | 30% | 2,975 (after 15%) | 7% |
| Aquarium shop dealer | 30% | 2,625 (after 25%) | −6% (loss) |
| Wholesale (B2B to chain) | 10% | 2,800 | 1% |
| **Blended realisation** | | **₹3,010** | **8%** |

The dealer channel is a drag until qty ≥ 1000 — keep the V2 channel mix
D2C-heavy (own website + Amazon) or raise dealer price.

---

## 5. Cash flow projection (12-month, V2 phase)

| Month | Action | Outflow ₹ | Inflow ₹ | Net ₹ |
|-------|--------|-----------|----------|-------|
| 1 | Order 100 units (MCPCB + components) | 3,30,000 | 0 | –3,30,000 |
| 2 | Assemble, test, photograph | 20,000 | 0 | –20,000 |
| 3 | Launch D2C, sell 20 units | 0 | 70,000 | +70,000 |
| 4 | Sell 30 units | 0 | 1,05,000 | +1,05,000 |
| 5 | Sell 30 units | 0 | 1,05,000 | +1,05,000 |
| 6 | Order 200 more units | 5,55,000 | 0 | –5,55,000 |
| 7 | Assemble + sell 40 | 10,000 | 1,40,000 | +1,30,000 |
| 8 | Sell 50 | 0 | 1,75,000 | +1,75,000 |
| 9 | Sell 60 | 0 | 2,10,000 | +2,10,000 |
| 10 | Order 200 more units | 5,55,000 | 0 | –5,55,000 |
| 11 | Sell 70 | 0 | 2,45,000 | +2,45,000 |
| 12 | Sell 80 + dealer channel | 0 | 3,00,000 | +3,00,000 |
| **12-month total** | **430 units** | **14,70,000** | **13,50,000** | **–120,000** |

Marginally negative with LEDs in the BOM — assumes owner-operator with no
salary draw. Realistic with one full-time person: would need ~700 units/year
at ₹3,500 retail to pay one salary + rent. Pure-D2C mix recovers first; the
dealer channel is the drag until qty ≥ 1000.

---

## 6. Volume milestones

| Milestone | Cumulative units | When (estimated) |
|-----------|-------------------|------------------|
| V0 prototype | 1 | Q1 2026 |
| V1 alpha (in-house demos) | 10 | Q2 2026 |
| V1 beta (community reviewers) | 50 | Q3 2026 |
| V1 small launch | 200 | Q4 2026 |
| V2 Indian production | 1,000 | Q2 2027 |
| V3 cost-down | 5,000 | Q4 2027 |

---

## 7. Demand assumptions (Indian market)

- India ornamental-fish hobbyists: ~2,000,000 households (rough estimate)
- Annual aquarium-light replacement market: ~150,000 units
- TICA Color Up India sales (estimate): ~3,000–5,000 units/year
- Chihiros India sales: ~2,000 units/year
- **Realistic V2 market share at 1,000 units/year: 0.5–0.7% of replacement**

Capturing 1% of the replacement market = 1,500 units/year = ₹5 Cr
revenue, ₹2 Cr gross profit. That's a small, healthy business.
