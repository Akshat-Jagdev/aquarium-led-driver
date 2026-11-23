# LCSC Direct Links — Aquarium V0 Components

> All links are direct to LCSC product pages. Search by part number if link breaks.
> Prices are approximate and change daily. Check at order time.
> Order total must exceed $50 (~₹4,000) for free shipping, otherwise add $5-10.

---

## Driver IC

**AL8860W6-7** — Diodes Inc, SOT23-6, 40V 1.5A Buck LED Driver
- LCSC P/N: **C460356**
- Search: https://www.lcsc.com/search?q=AL8860W6-7
- Direct: https://www.lcsc.com/product-detail/C460356.html
- Price: ~$0.35 (₹28) each
- Order 10 (1 spare for prototype)

---

## Schottky Diode

**SS3100** — Diodes Inc, 100V 3A Schottky, SMA
- LCSC P/N: **C2480**
- Search: https://www.lcsc.com/search?q=SS3100
- Direct: https://www.lcsc.com/product-detail/C2480.html
- Price: ~$0.20 (₹18) each
- Order 10
- **NOTE**: Do NOT use SS24 (40V) — voltage margin too tight

---

## Inductor

**Würth 7447783680** — WE-PD series, 68µH 0.95A shielded
- LCSC P/N: **C184706**
- Search: https://www.lcsc.com/search?q=7447783680
- Direct: https://www.lcsc.com/product-detail/C184706.html
- Price: ~$0.55 (₹45) each
- Order 10

**Alternative**: Bourns SRR1280-680M (LCSC search by name)

---

## Input Capacitor (ceramic, 22µF/50V X7R 1210)

**Murata GRM32ER71H226KE15L**
- LCSC P/N: **C13753**
- Search: https://www.lcsc.com/search?q=GRM32ER71H226KE15L
- Direct: https://www.lcsc.com/product-detail/C13753.html
- Price: ~$0.22 (₹18) each
- Order 10
- **CRITICAL**: Do NOT use 10µF 0805 — DC-bias derating makes it ineffective

---

## Bypass Capacitors

**100nF / 50V X7R 0603** (Samsung CL10B104KB8NFNC)
- LCSC P/N: **C346191**
- Price: ~$0.01 each
- Order 100 (very cheap)

**1µF / 50V X7R 0805** (Samsung CL21B105KBFNNNE)
- LCSC P/N: **C28323**
- Price: ~$0.02 each
- Order 20

---

## Current Sense Resistors (Vishay WSL2512)

**WSL2512R4000FEA** (0.40Ω 1% 1W) — White channels
- LCSC P/N: **C2990117**
- Price: ~$0.22 (₹18) each
- Order 10

**WSL2512R8200FEA** (0.82Ω 1% 1W) — Red and Deep-Red channels
- LCSC P/N: **C2990150**
- Price: ~$0.22 (₹18) each
- Order 5

**WSL2512R3300FEA** (0.33Ω 1% 1W) — Blue channel
- LCSC P/N: **C2990101**
- Price: ~$0.22 (₹18) each
- Order 3

---

## Standard Resistors 0603

**1kΩ 1% 0603** (Yageo RC0603FR-071KL)
- LCSC P/N: **C25804**
- Price: ~$0.01 each
- Order 20

**100kΩ 1% 0603** (Yageo RC0603FR-07100KL)
- LCSC P/N: **C25866**
- Price: ~$0.01 each
- Order 20

---

## Fuse

**Littelfuse 0215002.MXP** (2A 250V slow-blow, 5×20mm)
- LCSC P/N: **C190099**
- Price: ~$0.12 (₹10) each
- Order 5

**Fuse clip 5×20mm** (Keystone 3527 or equiv)
- LCSC P/N: **C92413**
- Price: ~$0.06 each
- Order 4

---

## LDO Regulator (for ESP32 3.3V)

**AMS1117-3.3** (Diodes Inc, SOT223)
- LCSC P/N: **C6186**
- Price: ~$0.12 (₹10) each
- Order 5

---

## Bulk Electrolytic

**Nichicon UPW1H221MPD** (220µF 50V, radial)
- Not on LCSC — buy from **Element14 India** or **Mouser India**
- Element14: https://in.element14.com (search "UPW1H221MPD")
- Price: ₹20-30 each
- Order 3

---

## Total LCSC Order Estimate (prototype)

| Part | Qty | Subtotal |
|------|-----|----------|
| AL8860W6-7 | 10 | ₹280 |
| SS3100 | 10 | ₹180 |
| 7447783680 | 10 | ₹450 |
| 22µF 1210 | 10 | ₹180 |
| 100nF 0603 | 100 | ₹100 |
| 1µF 0805 | 20 | ₹40 |
| WSL 0.40 | 10 | ₹180 |
| WSL 0.82 | 5 | ₹90 |
| WSL 0.33 | 3 | ₹54 |
| Resistors 1k | 20 | ₹20 |
| Resistors 100k | 20 | ₹20 |
| Fuse + clips | 5 + 4 | ₹75 |
| AMS1117-3.3 | 5 | ₹50 |
| **TOTAL** | | **₹1,719** |

Shipping to India: Free (over $50)
Customs/duty: ~10-15% if not prepaid (DDP)

---

## Cart-Building Shortcut

Copy-paste these LCSC P/N into the LCSC search box to add to cart:

```
C460356  (AL8860, x10)
C2480    (SS3100, x10)
C184706  (Wurth 68uH, x10)
C13753   (22uF 1210, x10)
C346191  (100nF 50V 0603, x100)
C28323   (1uF 50V 0805, x20)
C2990117 (WSL 0.40, x10)
C2990150 (WSL 0.82, x5)
C2990101 (WSL 0.33, x3)
C25804   (1k 0603, x20)
C25866   (100k 0603, x20)
C190099  (Fuse 2A, x5)
C92413   (Fuse clip, x4)
C6186    (AMS1117-3.3, x5)
```

Then separately order the electrolytic from Element14 India.
