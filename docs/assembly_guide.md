# Assembly Guide — AQUARIUM V0 Prototype
================================================================================

This document provides step-by-step instructions for assembling the V0 engineering 
prototype of the ColorBoost Aquarium LED system.

## 1. Prerequisites
### Tools Required:
- Soldering iron + solder (fine tip)
- Flux pen / solder paste
- Tweezers (ESD safe)
- Screwdriver (M3 size)
- Vernier caliper / Ruler
- Multimeter

### Component Checklist:
- [ ] C-channel Aluminium Profile (600mm)
- [ ] Driver PCB (V0)
- [ ] 4x MCPCB LED Arrays (2x Left-type, 2x Right-type)
- [ ] ESP32-C3 SuperMini
- [ ] All SMD components for Driver PCB (solder if not PCBA)
- [ ] Thermal pads (GP1500 or equivalent)
- [ ] M3 screws (6mm length) and nuts/taps
- [ ] DC Barrel Jack, Fuse, and Rocker Switch

---

## 2. Step-by-Step Assembly

### Phase A: Driver PCB Population
1. **SMD Assembly**: Solder all components onto the Driver PCB.
   - Pay close attention to the **AL8860 switching loop** (Inductor → Diode → AL8860).
   - Ensure decoupling capacitors (100nF and 22uF) are placed as close as possible to the VIN pins.
   - Solder the **RSET resistors** (0.40Ω, 0.82Ω, 0.33Ω) precisely; these determine the LED current.
2. **Controller Installation**: Solder the ESP32-C3 SuperMini to the J6 header or install via sockets.
3. **Power Stage**: Solder the DC jack, fuse clips, and switch.

### Phase B: Mechanical Preparation
1. **Degreasing**: Clean the inside of the C-channel web with Isopropyl Alcohol (IPA).
2. **Drilling**:
   - Mark 4x M3 holes per MCPCB location (16 holes total) based on the `extrusion_dims.md` map.
   - Drill and tap the holes into the aluminium web.
3. **Thermal Interface**: Cut 4x thermal pads to fit the MCPCB dimensions. Apply them to the aluminium web.

### Phase C: LED Integration
1. **MCPCB Mounting**: Bolt the 4 MCPCBs to the C-channel.
   - Order: L1, L2, R1, R2 (left to right).
   - Ensure they are centered and the 2mm gaps are maintained.
2. **Wiring**:
   - Connect the 6-pin headers from each MCPCB to the Driver PCB.
   - **Critical**: Verify the polarity (+/-) for each string (White, Red, Colour).
   - Route wires along the C-channel, ensuring they do not interfere with the diffuser.

### Phase D: Final Assembly
1. **Driver Mounting**: Secure the Driver PCB to the C-channel using M3 standoffs.
2. **Diffuser Install**: Snap the opal diffuser into the C-channel profile.
3. **Closure**: Install the aluminium end-caps to seal the unit.
4. **Brackets**: Attach the adjustable rim brackets to the ends of the extrusion.

---

## 3. First-Power Procedure (Safety First)
**DO NOT connect LEDs for the first power-up.**

1. **Continuity Check**: Use a multimeter to verify no shorts between +24V and GND.
2. **Control Power**: Apply 24V. Check if the ESP32 powers up (LED on board) and the 5V/3.3V rails are stable.
3. **Channel Test**:
   - Connect one LED string at a time.
   - Use the Serial Monitor to trigger "White Only" and verify the AL8860 output.
   - Repeat for Red, Blue, and Deep Red.
4. **Full Load**: Connect all strings and run the "Daylight" profile for 5 minutes.

---

## 4. Thermal Soak Test (TP-04)
1. Set the controller to "All Channels" (Maximum power).
2. Run for **2 hours** continuously.
3. Measure temperature at the center of each MCPCB using a thermocouple or IR thermometer.
4. **Pass Criteria**: MCPCB case temperature < 85°C.
================================================================================
