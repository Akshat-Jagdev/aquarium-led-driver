# KiCad Design Specifications — ORNAMENTAL V0

This document serves as the final a-priori specification for the KiCad 8 project. All dimensions are final based on the "Recommended" configuration choice (60 cm, Opal, Rim-mount).

## 1. Global Constraints
- **Project Goal**: ColorBoost V0 Driver & LED Array
- **Input Power**: 24 V DC (via DC Barrel Jack)
- **Total Length**: 600 mm
- **Max Width (Driver Strip)**: 14 mm (Hard constraint for 80x20 extrusion cavity)
- **Max Length (Driver Strip)**: 580 mm
- **PCB Layers**: 2-layer, 1 oz copper
- **Manufacturer**: JLCPCB (Default settings: 0.15mm trace/space)

## 2. Component Layout (The Driver Strip)
The board is a long slender strip containing 7× AL8860 buck drivers and an ESP32-C3 control section.

### 2.1 Power Section (One End)
- **Input**: DC Barrel Jack (2.1mm) $\rightarrow$ Fuse $\rightarrow$ Rocker Switch.
- **Regulation**: 24V $\rightarrow$ 3.3V for ESP32 (LDO/Buck).
- **Isolation**: Keep 3.3V section $\ge 10\text{mm}$ away from AL8860 switching nodes.

### 2.2 Driver Section (The Array)
7× AL8860 drivers arranged linearly.
- **Switching Loop (CRITICAL)**: $\text{LX} \rightarrow \text{Inductor} \rightarrow \text{Diode Anode} \rightarrow \text{Diode Cathode} \rightarrow \text{VIN}$.
  - Loop must be as small as possible.
  - All three (IC, L, D) on the top layer.
  - Catch-diode anode trace must be under the inductor.
- **Decoupling**:
  - 100 nF (0603) within 2 mm of VIN pin.
  - 22 $\mu$F (1210) within 5 mm of VIN pin on the same copper pour.
- **Thermal**: $\ge 100\text{mm}^2$ copper pour on both layers under each IC, stitched with 8-12 thermal vias.

### 2.3 Connectors (MCPCB Headers)
4× 6-pin headers (J2-J5) spaced to align with MCPCBs.
- **Pinout (per header)**:
  - Pin 1: White Anode ($\text{LX}_{white}$)
  - Pin 2: White Cathode $\rightarrow \text{RSET} \rightarrow \text{GND}$
  - Pin 3: Red Anode
  - Pin 4: Red Cathode
  - Pin 5: Color Anode (Blue or Deep-Red)
  - Pin 6: Color Cathode
- **Routing**:
  - $\text{White traces} \ge 1\text{mm}$ width.
  - $\text{Red/Blue/DR traces} \ge 0.5\text{mm}$ width.
  - Keep anode/cathode traces adjacent.

## 3. Mechanical Integration
- **Housing**: 80x20 Aluminium Extrusion (600 mm).
- **MCPCBs**: 4× 140x20 mm boards.
  - 2× Left-design (White, Red, Blue)
  - 2× Right-design (White, Red, Deep-Red)
- **Mounting**: Rim-mount brackets (to be designed in mechanical STEP files).
- **Diffuser**: Opal (Full length, sliding into extrusion).

## 4. DRC Checklist
- [ ] Min trace/space: 0.15 mm
- [ ] Min via drill: 0.3 mm / Pad: 0.5 mm
- [ ] Edge clearance: 0.3 mm
- [ ] Ground: Single unbroken pour on bottom layer.
- [ ] CTRL traces: Routed on opposite layer from 24V switching traces.
