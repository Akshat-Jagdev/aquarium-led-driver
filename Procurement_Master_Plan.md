# 🛒 Aquarium V0 Procurement Master Plan
This is your verified shopping list. Do not try to buy everything from one site; use the sources listed below to ensure you get the correct parts for the prototype.

## 🟦 Source 1: LCSC Electronics (The SMD Kit)
**File to Upload:** `LCSC_Verified_SMD.csv`
These are the components that go on the PCB. LCSC is the cheapest and fastest for these.

| Component | Verified LCSC Part # | Qty |
| :--- | :--- | :--- |
| AL8860 Driver | `C125330` | 7 |
| SS310 Diode | `C717452` | 7 |
| White 5050 LED | `C17340841` | 12 |
| Red 2835 LED | `C17179636` | 4 |
| Royal Blue 2835 LED | `C17488383` | 2 |
| Deep Red 2835 LED | `C22447975` | 2 |
| 68uH Inductor | `C116274` | 7 |
| 22uF Capacitor | `C15331` | 7 |
| 100nF Capacitor | `C14612` | 14 |
| 1uF Capacitor | `C14613` | 7 |

---

## 🟧 Source 2: AliExpress (The Modules)
LCSC sells the raw ESP32 chip, but for a prototype, you need the **breakout board**.

| Item | Search Term on AliExpress | Qty | Note |
| :--- | :--- | :--- | :--- |
| **ESP32-C3 SuperMini** | "ESP32-C3 SuperMini" | 1 | Look for the tiny board with USB-C |

---

## 🟩 Source 3: Amazon India / Local Hardware (Power & Frame)
These are too heavy/bulky for LCSC or DigiKey.

| Item | Where to Buy | Search Term / Spec | Qty |
| :--- | :--- | :--- | :--- |
| **Main PSU** | Amazon.in / Local | "Mean Well LRS-35-24" | 1 |
| **DC-DC Converter** | Amazon.in / Local | "Mean Well IRM-02-5" (24V to 5V) | 1 |
| **Alu Extrusion** | Local Hardware | "6063 Aluminium Profile" (600mm) | 1 |
| **Acrylic Sheet** | Local Plastic Shop | "3mm Opal Acrylic" (Diffuser) | 1 |
| **DC Jack** | Local / Amazon | "2.1mm Panel Mount DC Jack" | 1 |
| **Rocker Switch** | Local / Amazon | "3A Rocker Switch Panel Mount" | 1 |
| **Fuse & Clips** | Local / Amazon | "2A Slow Blow Fuse 5x20mm" + Clips | 1 set |

---

## 🟥 Source 4: JLCPCB (The Boards)
You cannot buy these "off the shelf"; they must be manufactured using the design files.

| Item | Order From | Specification | Qty |
| :--- | :--- | :--- | :--- |
| **Driver PCB** | JLCPCB | 4-layer PCB, 1.6mm FR4 | 5 pcs |
| **MCPCBs** | JLCPCB | Aluminium Core PCB, 140x20mm | 4 pcs |

---

### ✅ Final Checklist for You:
1. [ ] Upload `LCSC_Verified_SMD.csv` to **LCSC**.
2. [ ] Order the **ESP32-C3 SuperMini** from **AliExpress**.
3. [ ] Order the **Power Supply** and **Mechanicals** from **Amazon/Local**.
4. [ ] Upload the KiCad files to **JLCPCB** for the boards.
