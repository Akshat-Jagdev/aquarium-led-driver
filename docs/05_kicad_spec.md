# KiCad Specification — COLORBOOST V0
> Master blueprint for schematic capture and PCB layout of the V0 prototype.

---

## 1. Project Overview
- **KiCad Version**: 8.0
- **Board Architecture**: Hybrid system.
  - **Driver Board**: One slender strip PCB containing 7x AL8860 circuits and the ESP32 controller.
  - **MCPCBs**: 4x LED boards (140x20mm) with thermal pads.
- **Input**: 24V DC (via Mean Well LRS-35-24).
- **Logic**: 3.3V (via IRM-02-5 + AMS1117-3.3).

---

## 2. Schematic Requirements

### 2.1 Power Input Section
- **Connector**: 2.1mm DC Barrel Jack $\rightarrow$ Rocker Switch $\rightarrow$ 2A Slow-blow Fuse $\rightarrow$ 24V BUS.
- **Bulk Filtering**:
  - 220µF/50V Low-ESR Electrolytic (Nichicon UPW) near input.
  - 100nF X7R 0603 Ceramic for high-frequency noise.

### 2.2 Logic Power (ESP32)
- **Converter**: 24V $\rightarrow$ 5V (Mean Well IRM-02-5).
- **LDO**: 5V $\rightarrow$ 3.3V (AMS1117-3.3) with 1µF input/output caps.
- **Connection**: 3.3V $\rightarrow$ ESP32-C3 SuperMini VIN/3.3V pin.

### 2.3 Driver Circuit (The "AL8860 Cell")
*Replicate this block 7 times (4 White, 1 Red, 1 Blue, 1 Deep-Red).*

- **VIN Pin (6)**: Local 100nF + 22µF (1210 case) bypass caps.
- **LX Pin (1)**: 68µH Shielded Inductor $\rightarrow$ LED Anode.
- **Flyback Diode**: SS3100 SMA Schottky (Anode @ LX, Cathode @ 24V BUS).
- **CTRL Pin (5)**: 1kΩ series resistor from ESP32 GPIO $\rightarrow$ 100kΩ pull-down to GND.
- **CS Pin (4)**: $\rightarrow$ RSET $\rightarrow$ LED Cathode $\rightarrow$ GND.

### 2.4 LED String Definitions
| Channel | Qty | LED Type | RSET Value | Total Vf (est) | Current |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **White (x4)** | 3 | Luxeon 5050 HE | 0.40Ω | 17.55V | 250mA |
| **Red (x1)** | 4 | Luxeon 2835 Red | 0.82Ω | 8.4V | 120mA |
| **Blue (x1)** | 2 | Luxeon Rubix | 0.33Ω | 6.32V | 303mA |
| **Deep Red (x1)** | 2 | Luxeon SunPlus | 0.82Ω | 4.30V | 120mA |

---

## 3. PCB Layout Strategy

### 3.1 Driver Board (The "Control Strip")
- **Dimensions**: Max width $\le$ 14mm to fit extrusion cavity.
- **Stackup**: 2-layer, 1.6mm FR4.
- **Critical Layout**:
  - **The Switching Loop**: Keep the loop between AL8860 (LX), Inductor, and Schottky diode as small as possible.
  - **Grounding**: Solid bottom-layer GND plane. Use "star ground" or wide pours for the RSET returns.
  - **Thermal**: Add copper pours (vias to bottom) under each AL8860 SOT23 package.
  - **Routing**: 24V traces $\ge$ 0.5mm; LED return traces $\ge$ 0.5mm.

### 3.2 MCPCBs (The "Light Engines")
- **Dimensions**: 140 x 20 mm.
- **Material**: Aluminium MCPCB (1W/mK+).
- **Arrangement**: 5 LEDs per board, 28mm pitch.
- **Interconnects**:
  - Use 2-pin JST-PH or similar connectors for string jumps.
  - Red string jumps across all 4 boards. Blue/Deep-Red jump across 2 boards each.

---

## 4. Component Footprint Map
- **AL8860**: SOT23-6.
- **Inductor**: 7447783680 (Custom footprint based on datasheet).
- **RSET**: Resistor_SMD:R_2512_6332Metric.
- **Diode**: Diode_SMD:D_SMA.
- **Caps**: 0603 (100nF), 1210 (22µF).
- **ESP32-C3**: Custom footprint for "SuperMini" module.
