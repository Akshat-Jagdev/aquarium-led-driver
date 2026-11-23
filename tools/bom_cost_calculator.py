"""
AQUARIUM V0 LED LIGHT — BOM COST CALCULATOR
============================================

Calculates the cost of one unit based on your local component pricing.
Edit the PRICE_INR values to match what you actually pay.

Goal: get production BOM <= ₹2,000 per unit.
Target retail: ₹3,000-4,000.
"""

# ============================================================
#  EDIT PRICES HERE (in Indian Rupees)
# ============================================================

# (Part, Quantity, Unit Price INR, Notes)
PARTS = [
    # Drivers
    ("AL8860W6-7",         7,  28,  "Diodes buck LED driver, LCSC"),
    ("SS3100 Schottky",    7,  18,  "100V/3A, SMA"),
    ("Würth 68µH 7447783680", 7, 45, "WE-PD series shielded, LCSC"),
    ("22µF/50V X7R 1210",  7,  18,  "Murata GRM32ER71H226KE15L"),
    ("100nF/50V X7R 0603", 14,  1,  "Generic"),
    ("1µF/50V X7R 0805",   7,   2,  "AMS1117 caps + optional CS filter"),

    # Current sense resistors
    ("0.40Ω 1% 2512 (W)",  4,  18,  "WSL2512R4000FEA"),
    ("0.82Ω 1% 2512 (R,DR)",2,  18,  "WSL2512R8200FEA"),
    ("0.33Ω 1% 2512 (B)",  1,  18,  "WSL2512R3300FEA"),

    # Control
    ("ESP32-C3 SuperMini", 1,  250, "Alibaba/Amazon India"),
    ("1kΩ 0603",           4,   1,  "Yageo"),
    ("100kΩ 0603",         4,   1,  "Yageo"),

    # Power input
    ("Mean Well LRS-35-24",1,  450, "ConvertersIndia / Sunrom"),
    ("DC barrel jack",     1,   30, "Panel mount"),
    ("Rocker switch 3A",   1,   25, "Panel mount"),
    ("2A slow-blow fuse",  1,   10, "5x20mm"),
    ("Fuse clips",         2,    5, "Keystone 3527 or equiv"),
    ("220µF/50V electrolytic",1, 25, "Nichicon UPW1H221MPD"),
    ("DC-DC 24V->5V isol", 1,  150, "Mean Well IRM-02-5 or RECOM"),

    # Mechanical
    ("LED MCPCB 140x20mm 5-LED (2 designs x2)", 4, 120, "JLCPCB/Indian fab"),
    ("Al extrusion 6063", 1,  400, "Local hardware store, ~600mm"),
    ("Thermal pad 3W/mK", 1,  100, "Bergquist GP1500 or generic"),
    ("Acrylic diffuser opal 3mm", 1, 200, "Local plastic supplier"),
    ("End caps",           2,  30, "3D printed or aluminium"),
    ("Mounting brackets",  2,  80, "Stainless or aluminium"),

    # PCB itself
    ("2-layer PCB V0",     1,  150, "JLCPCB or PCBWay, 5 PCBs / 5 = 30/unit"),
    # Assembly consumables
    ("Solder paste, wire, misc", 1, 50, "Per-unit allocation"),
]

# ============================================================
#  CALCULATIONS
# ============================================================

def main():
    print("="*68)
    print(" AQUARIUM V0 — BOM COST (Prototype, 1 unit)")
    print("="*68)
    print(f"{'Part':<32} {'Qty':>4} {'Unit ₹':>9} {'Total ₹':>10}")
    print("-"*68)

    total = 0
    for name, qty, price, notes in PARTS:
        line = qty * price
        total += line
        print(f"{name:<32} {qty:>4} {price:>9} {line:>10}")

    print("-"*68)
    print(f"{'TOTAL per unit (qty 1)':<32} {'':>4} {'':>9} {total:>10}")
    print()

    # At volume 100, 500, 1000
    print("="*68)
    print(" ESTIMATED COST AT VOLUME")
    print("="*68)
    # Volume discount: drivers, passives, MCPCB get cheaper
    # MCPCB drops to ~₹70 at 500 units
    # AL8860 drops to ~₹15 at 1000 units
    # ESP32-C3 drops to ~₹180 at 1000 units
    # LRS-35-24 drops to ~₹380 at 500 units
    vol_discount = {
        1: 1.00,
        100: 0.80,
        500: 0.65,
        1000: 0.55,
    }
    for vol, factor in vol_discount.items():
        cost = total * factor
        print(f" Volume {vol:>5} units: ₹{cost:.0f} per unit (target: <₹2,000)")
    print()

    # Margin at ₹3,500 retail
    print("="*68)
    print(" MARGIN AT ₹3,500 RETAIL")
    print("="*68)
    for vol, factor in vol_discount.items():
        cost = total * factor
        margin = 3500 - cost
        margin_pct = (margin / 3500) * 100
        print(f" Volume {vol:>5}: cost ₹{cost:.0f}, margin ₹{margin:.0f} ({margin_pct:.1f}%)")
    print()
    print(" Targets:")
    print(" - V0 prototype: cost doesn't matter, focus on engineering")
    print(" - V1 (100 units): aim for <₹2,500 per unit")
    print(" - V2 (500+ units): aim for <₹2,000 per unit")
    print(" - V3 (1000+ units): aim for <₹1,500 per unit")

if __name__ == "__main__":
    main()
