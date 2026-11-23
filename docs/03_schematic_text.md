# V0 Schematic — Text Form

> This is a text representation of the V0 schematic. Use it as a reference when:
> 1. Wiring the one-channel perfboard prototype (Phase B)
> 2. Capturing the schematic in KiCad (Phase C)
> 3. Reviewing the PCB layout

---

## 1. Power Input

```
                          [F1 2A slow-blow]
                              5x20mm
                                |
[24V PSU+] ──[F1]───────────────┬──────────────────── 24V BUS (+)
                                |
                          [100nF X7R 0603]
                          C_bulk_ceramic
                                |
[24V PSU-] ─────────────────────┴──────────────────── 24V GND / BUS (-)


Across 24V BUS, near PSU input:

       [+24V BUS]    [+24V BUS]
            |             |
        [220uF/50V]   [100nF X7R 0603]
            |             |
            └─────┬───────┘
                  |
                GND
```

---

## 2. ESP32 Power Supply

> ⚠ **CORRECTION (2026-09-10).** The Mean Well IRM-02-5 is an
> **85–264 VAC** input module — it cannot convert 24 VDC, so this
> chain does not work as drawn. **V0 decision:** leave U8/U9/C3/C4
> unpopulated and power the ESP32 SuperMini from its own USB port
> (the fallback already noted below); J6 still carries the PWM
> signals + GND. **V1 must use a real 24 V→5 V DC-DC** (e.g. Recom
> R-78E5.0-0.5 buck, SIP-3) ahead of the AMS1117-3.3.

```
24V BUS (+) ──[Mean Well IRM-02-5]── 5V BUS ──[AMS1117-3.3]── 3.3V BUS
                                                |
                                              [1uF] [1uF]
                                                |    |
                                                GND  GND

ESP32-C3 SuperMini:
  VIN  → 5V BUS (or use 3.3V pin)
  GND  → 24V GND (common)
```

**Note**: If using USB-powered ESP32 (not from PSU), you can simplify by using a USB-C charger and skip the IRM-02-5 + AMS1117.

---

## 3. Generic AL8860 Driver Circuit (×7)

```
                [100nF X7R 0603]    [22uF/50V X7R 1210]
24V BUS (+) ────┬──[C]──┬───────────┬──[C]──┬────── VIN (pin 6)
                │        │           │       │
                │        │           │       │
                │        │           │       │  VIN  (AL8860)
                │        │           │       │
                │        │           │       └────── pin 6
                │        │           │
                │        │           │   [CTRL pin 5]
                │        │           │        │
                │        │           │   [100kΩ 1% 0603]
                │        │           │        │
                │        │           │       GND
                │        │           │
                │        │           └─────── GND (pin 2)
                │        │
                │        └────────── GND
                │
                └────────── GND
                

Switching node:

    VIN (pin 6)
         |
    LX (pin 1) ───[68uH 7447783680]──┬── to LED string ANODE
                                     │
                              [D1: SS3100 100V/3A SMA]
                              Anode at LX
                              Cathode to 24V BUS (i.e., to VIN)
                              
Current sense:

    GND ── CS (pin 4) ──[RSET 2512]── to LED string CATHODE ── returns to GND
```

---

## 4. LED String Wiring (each channel)

### 4.1 White Channels (×4 identical)

```
                [3x White LEDs in series]
                
LX node ──[68uH]──┬─── LED 1 ANODE (LED 1: 5050 HE Plus 5700K)
                   |
                   ├─── LED 2 ANODE (-- LED 1 CATHODE)
                   |
                   ├─── LED 3 ANODE (-- LED 2 CATHODE)
                   |
                   └─── [RSET 0.40Ω 2512]── GND (-- LED 3 CATHODE)


Current per string: 250 mA
Power per string: 17.55V × 0.250A = 4.39 W
Total white power: 4.39 × 4 = 17.6 W
```

### 4.2 Red Channel (×1)

```
LX node ──[68uH]──┬─── LED 1 ANODE (2835 Red 625nm)
                   |
                   ├─── LED 2 ANODE
                   |
                   ├─── LED 3 ANODE
                   |
                   ├─── LED 4 ANODE
                   |
                   └─── [RSET 0.82Ω 2512]── GND


Current: 120 mA
Power: 8.4V × 0.120A = 1.01 W
```

### 4.3 Blue Channel (×1)

```
LX node ──[68uH]──┬─── LED 1 ANODE (Rubix 448nm)
                   |
                   ├─── LED 2 ANODE
                   |
                   └─── [RSET 0.33Ω 2512]── GND


Current: 303 mA (start conservative, can increase to 333 mA later)
Power: 6.32V × 0.303A = 1.91 W
```

### 4.4 Deep Red Channel (×1)

```
LX node ──[68uH]──┬─── LED 1 ANODE (SunPlus 660nm)
                   |
                   ├─── LED 2 ANODE
                   |
                   └─── [RSET 0.82Ω 2512]── GND


Current: 120 mA
Power: 4.30V × 0.120A = 0.52 W
```

---

## 5. ESP32-C3 Pin Assignment

```
ESP32-C3 SuperMini
    ├── GPIO 0  ──[1kΩ]──┬── CTRL of WHITE_DRV1
    │                     ├── CTRL of WHITE_DRV2
    │                     ├── CTRL of WHITE_DRV3
    │                     ├── CTRL of WHITE_DRV4
    │                     └── 100kΩ to GND (at first driver)
    │
    ├── GPIO 1  ──[1kΩ]──┬── CTRL of RED_DRV
    │                     └── 100kΩ to GND
    │
    ├── GPIO 2  ──[1kΩ]──┬── CTRL of BLUE_DRV
    │                     └── 100kΩ to GND
    │
    ├── GPIO 3  ──[1kΩ]──┬── CTRL of DEEPRED_DRV
    │                     └── 100kΩ to GND
    │
    ├── 5V or 3V3  ── from 24V→5V DC-DC + AMS1117-3.3
    │              OR  from USB charger (if separate)
    │
    ├── GND  ── 24V GND (common)
    │
    └── (USB-C)  ── for programming and serial monitor
```

**IMPORTANT**: There is **no 2N7002** in the corrected design. The ESP32 GPIO drives AL8860 CTRL directly through 1 kΩ.

---

## 6. ESP32-C3 SuperMini Pin Reference

The ESP32-C3 SuperMini has these usable GPIOs (avoid strapping pins):
- **Safe to use**: GPIO 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 18, 19, 20, 21
- **Avoid (strapping)**: GPIO 2 (already in use for boot mode), GPIO 8, GPIO 9
- **Use for onboard LED**: GPIO 8 (status indicator)

For this project, we use GPIO 0, 1, 2, 3 for the 4 LED channels. GPIO 2 is technically a strapping pin but works for PWM after boot.

**Alternative if GPIO 2 causes issues**: Use GPIO 10 for blue channel instead.

---

## 7. Full Bill of Materials (per channel type)

### 7.1 Per White Channel (×4 total)
- 1× AL8860W6-7
- 1× Würth 7447783680 (68 µH)
- 1× SS3100 (Schottky)
- 1× 22 µF/50V X7R 1210
- 1× 100 nF X7R 0603
- 1× WSL2512R4000FEA (0.40 Ω RSET)
- 3× LUXEON 5050 HE Plus 5700K

### 7.2 Per Red Channel (×1)
- 1× AL8860W6-7
- 1× Würth 7447783680
- 1× SS3100
- 1× 22 µF/50V X7R 1210
- 1× 100 nF X7R 0603
- 1× WSL2512R8200FEA (0.82 Ω)
- 4× LUXEON 2835 Red 625 nm

### 7.3 Per Blue Channel (×1)
- 1× AL8860W6-7
- 1× Würth 7447783680
- 1× SS3100
- 1× 22 µF/50V X7R 1210
- 1× 100 nF X7R 0603
- 1× WSL2512R3300FEA (0.33 Ω)
- 2× LUXEON Rubix 448 nm

### 7.4 Per Deep Red Channel (×1)
- 1× AL8860W6-7
- 1× Würth 7447783680
- 1× SS3100
- 1× 22 µF/50V X7R 1210
- 1× 100 nF X7R 0603
- 1× WSL2512R8200FEA (0.82 Ω)
- 2× LUXEON SunPlus 660 nm

### 7.5 ESP32 Interface (×4 channels)
- 4× 1 kΩ 0603
- 4× 100 kΩ 0603

### 7.6 Power Input
- 1× 220 µF/50V electrolytic (Nichicon UPW1H221MPD)
- 1× 100 nF X7R 0603
- 1× 2A slow-blow fuse
- 2× fuse clip
- 1× DC barrel jack 2.1mm
- 1× SPST rocker switch
- 1× Mean Well IRM-02-5 (24V → 5V) — ⚠ WRONG PART SPEC: IRM-02-5 needs
  85–264 VAC, not 24 VDC. V0: unpopulated (ESP32 USB-powered); V1: replace
  with a 24 V→5 V buck (e.g. Recom R-78E5.0-0.5) — see §2 correction.
- 1× AMS1117-3.3 LDO
- 2× 1 µF X7R 0805 (AMS1117 input/output)

---

## 8. PCB Layout Hints (for Phase C)

1. **Input capacitor placement**: 100 nF must be within 2 mm of AL8860 VIN pin. 22 µF can be slightly further but still close.
2. **Switching loop**: Minimize the LX-to-inductor-to-diode-to-VIN loop. This is the high-di/dt loop.
3. **Ground pour**: Continuous ground plane on bottom layer. Connect CS RSET ground to this plane, NOT to a thin trace.
4. **Thermal copper**: ≥100 mm² copper pour under each AL8860 on both layers.
5. **LED strings**: Keep traces wide (≥1 mm) to handle LED current.
6. **Separation**: Keep 24 V input section away from 3.3 V ESP32 section.

---

## 9. KiCad Symbol/Component Notes

When you create the KiCad schematic:

- **AL8860**: Use the official Diodes Inc symbol. SOT23-6 footprint.
- **Würth inductor**: Search KiCad library for "WE-PD" or "7447783680". Add 3D model.
- **Vishay WSL2512**: Use "Resistor_SMD:R_2512_6332Metric" footprint.
- **SS3100**: Use "Diode_SMD:D_SMA" footprint.
- **ESP32-C3 SuperMini**: Not a standard KiCad symbol. Create a custom symbol + footprint module.
- **LEDs**: Create custom symbols for LUXEON 5050 (with anode/cathode/pad) and 2835.

KiCad 8 has a "Symbol Editor" and "Footprint Editor" — use these to add custom parts.
