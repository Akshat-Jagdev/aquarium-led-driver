# Unit Economics — Aquarium V0 / COLORBOOST

> Per-unit cost, pricing, and margin model.
> Last updated: 2026-09-01 (LED cost folded into all production volumes)

---

## 1. Pricing assumptions

- **Retail price (target)**: ₹3,500 per unit (60 cm light)
- **Distributor margin** (if sold via dealer): 25%
- **Online D2C margin** (Amazon/Flipkart referral + shipping): 15%
- **Effective revenue per unit (D2C)**: ₹3,500 × 0.85 = ₹2,975
- **Effective revenue per unit (dealer)**: ₹3,500 × 0.75 = ₹2,625

---

## 2. BOM at prototype (qty 1)

From `bom/BOM_v0_prototype.csv`, total ₹3,591 including:

| Category | Cost (₹) | % |
|----------|----------|---|
| LEDs (already owned) | 0 | 0% |
| Drivers (AL8860, diode, inductor, caps) | 763 | 21% |
| ESP32 + passives | 254 | 7% |
| PSU (already owned) | 0 | 0% |
| Power components (fuse, switch, jack, DC-DC) | 245 | 7% |
| Mechanical (extrusion, MCPCB, thermal pad, acrylic, brackets) | 1,400 | 39% |
| PCB + assembly consumables | 200 | 6% |
| **Sub-total (excluding LEDs/PSU you already own)** | **₹2,862** | **80%** |
| Sunk cost: LEDs (12× 5050, 4× 2835R, 2× Rubix, 2× SunPlus) | ~₹1,000 | 28% |
| Sunk cost: PSU | ~₹450 | 12% |
| **Total "all-in" prototype cost** | **₹4,312** | 120% |

> At qty 1 you will *not* make money. That's expected — V0 is engineering, not business.

---

## 3. BOM at qty 100

Volume discounts expected:

| Part | qty 1 ₹ | qty 100 ₹ (–20%) |
|------|---------|-------------------|
| AL8860 (7×) | 196 | 157 |
| SS3100 (7×) | 126 | 101 |
| 68 µH (7×) | 315 | 252 |
| 22 µF 1210 (7×) | 126 | 101 |
| RSETs (7×) | 126 | 101 |
| ESP32-C3 | 250 | 200 |
| 1kΩ / 100kΩ (8) | 8 | 6 |
| PSU LRS-35-24 | 450 | 400 |
| IRM-02-5 | 150 | 130 |
| Fuse + clips | 20 | 16 |
| DC jack + switch | 55 | 45 |
| 220 µF electrolytic | 25 | 20 |
| AMS1117 + caps | 14 | 11 |
| MCPCB (4×) | 480 | 384 |
| Extrusion 6063 | 400 | 320 |
| Thermal pad | 100 | 80 |
| Acrylic diffuser | 200 | 160 |
| End caps | 60 | 48 |
| Brackets | 160 | 128 |
| PCB V0 (panelised) | 150 | 90 |
| Assembly consumables | 50 | 40 |
| LUXEON LED set (12W + 4R + 2B + 2DR) | ~1,000 | 510 |
| **TOTAL per unit (incl. LEDs)** | **₹4,463** | **₹3,300** |

**At qty 100, per-unit BOM ≈ ₹3,300 (incl. LEDs).** Margin at ₹3,500 D2C = (3,500 − 3,300) / 3,500 = **6%** — thin. Treat qty 100 as channel seeding, not profit.

---

## 4. BOM at qty 500

Same components, deeper discounts (–35% from qty 1):

| Component group | qty 500 ₹ per unit |
|-----------------|---------------------|
| Drivers + passives | 580 |
| ESP32 + control | 215 |
| Power section | 540 |
| Mechanical | 950 |
| PCB + consumables | 110 |
| LEDs (LUXEON set, 20 pcs) | 376 |
| **TOTAL per unit (incl. LEDs)** | **₹2,771** |

**At qty 500, BOM ≈ ₹2,771 (incl. LEDs).** Margin at ₹3,500 D2C = **21%**.
At ₹4,000 retail (margin push): **31%**.

> Cross-check: `bom/BOM_v0_production_500.csv` prices the same components
> more aggressively → **₹2,542/unit incl. LEDs**. The planning tables here
> use a slightly padded basis (the pre-existing ~₹225 gap); use the CSV for
> purchase budgets, these tables for margin planning.

---

## 5. BOM at qty 1000

Negotiated Indian fab pricing for MCPCB + PCB brings mechanical down further:

| Component group | qty 1000 ₹ per unit |
|-----------------|----------------------|
| Drivers + passives | 460 |
| ESP32 + control | 180 |
| Power section | 480 |
| Mechanical | 800 |
| PCB + consumables | 90 |
| LEDs (LUXEON set, 20 pcs) | 330 |
| **TOTAL per unit (incl. LEDs)** | **₹2,340** |

**At qty 1000, BOM ≈ ₹2,340 (incl. LEDs).** Margin at ₹3,500 D2C = **33%**.

---

## 6. Cost-out roadmap (qty 1000 → 5000)

To get below ₹1,500 per unit (ex-LEDs) / ₹1,800 (incl. LEDs):

1. **Negotiate LED pricing with a Lumileds distributor** (5050 HE Plus is the
   biggest single LED line; −₹40–90/unit at 5,000+)
2. **Replace ESP32-C3 SuperMini with bare ESP32-C3 module** (−₹120/unit)
3. **Drop IRM-02-5 → use USB-C PD trigger** (−₹70/unit, simpler BOM)
4. **Indian MCPCB fab** at 5,000+ units (−₹50/unit)
5. **Custom aluminium extrusion** (no off-the-shelf markup) (−₹100/unit)
6. **Move PSU to in-house Mean Well equivalent** (−₹50/unit, requires BIS)

Realistic target: **₹1,780 per unit at qty 5,000+** (≈₹1,500 bill-of-parts +
≈₹280 LED set at that volume). **The ₹2,000 BOM target is not reachable at
qty 500–1000 once LEDs are priced in; it clears around qty 5000+.**

---

## 7. Margin summary

| Volume | BOM ₹ (incl. LEDs) | D2C margin @ ₹3,500 | Dealer margin @ ₹3,500 |
|--------|---------------------|----------------------|------------------------|
| 1 (prototype) | 4,312 | –23% | –23% |
| 100 | 3,300 | 6% | –19% (loss) |
| 500 | 2,771 | 21% | –4% (loss) |
| 1000 | 2,340 | 33% | 8% |
| 5000 (target) | 1,780 | 49% | 24% |

**Dealer channel is unprofitable until qty ≥ 1000.** D2C is only marginal at
qty 100 (6%); healthy profit needs qty ≥ 500. The ₹2,000 BOM target is NOT
reachable at qty 500–1000 once LEDs are priced in.

---

## 8. Working capital

| Phase | Cash needed | Why |
|-------|-------------|-----|
| V0 prototype (1 unit) | ₹5,000 | Components + MCPCB samples |
| V1 pilot (10 units) | ₹40,000 | Enough for first dealer demo batch |
| V1 small batch (100 units) | ₹3,00,000 | Inventory + 30-day receivable from dealers |
| V2 (500 units) | ₹15,00,000 | Inventory + Amazon referral + GST float |

---

## 9. Tax / compliance impact on margin

- **GST**: 18% on aquarium electronics (HSN 9405)
- **Input Tax Credit (ITC)**: available on all components → net GST out ≈ 0% if registered
- **BIS registration**: ₹50,000–1,00,000 one-time (deferred to V2)
- **E-Waste (EPR)**: ₹5–10 per unit at production scale
- **Dealer commission**: usually 20–25%
- **Packaging + shipping**: ₹100–150 per unit (D2C), ₹60 (wholesale)

---

## 10. Pricing sensitivity

LED pricing is the swing factor at production volume (₹510 / ₹376 / ₹330 at
qty 100 / 500 / 1000). If the LED set lands 15% higher than forecast (+₹56 /
+₹50 at qty 500):

| Volume | Margin @ ₹3,500 D2C |
|--------|----------------------|
| 500 | 18% |
| 1000 | 30% |

If the 5050 white comes in ₹4 cheaper via direct negotiation (≈ −₹48/unit):

| Volume | Margin @ ₹3,500 D2C |
|--------|----------------------|
| 500 | 22% |
| 1000 | 34% |

If retail drops to ₹3,000 (competitive pressure):

| Volume | Margin @ ₹3,000 D2C |
|--------|----------------------|
| 500 | 8% (tight) |
| 1000 | 22% |
| 5000 | 41% |

**Conclusion**: stay above ₹3,500 retail. At ₹2,771 (qty 500) the product
works only D2C; the ₹2,000 BOM target is unreachable before ~qty 5000.

---

## 11. Bottom line

- V0 loses money. That's fine.
- V1 (qty 100) is thin: ~6% D2C, negative on dealer.
- V2 (qty 500+) is genuinely profitable (21% D2C).
- **LEDs add ₹376/unit at qty 500** — every production-volume BOM must
  include them.
- Target ₹3,500 retail, ~₹2,340 BOM (incl. LEDs) at qty 1000 → 33% D2C margin.
- The ₹2,000 BOM target is realistic only at ~qty 5000+ after LED and
  mechanical cost-out.
