# ESP32-C3 SuperMini Pin Assignment — V0

> Pin mapping between ESP32-C3 SuperMini GPIOs and the 4 LED channels.
> Drives 7 AL8860 CTRL pins (4 white share one GPIO).

## 1. Pin table

| GPIO | Function | Series R | Pull-down R | Drives |
|------|----------|----------|-------------|--------|
| GPIO 0 | White channel (all 4 in parallel) | 1 kΩ | 100 kΩ | CTRL of AL8860 #1–4 |
| GPIO 1 | Red channel | 1 kΩ | 100 kΩ | CTRL of AL8860 #5 |
| GPIO 2 | Blue channel | 1 kΩ | 100 kΩ | CTRL of AL8860 #6 |
| GPIO 3 | Deep-red channel | 1 kΩ | 100 kΩ | CTRL of AL8860 #7 |
| 5V | VBUS / VIN (when USB powered) | — | — | powers on-board 3V3 LDO |
| GND | Common ground | — | — | ties to 24 V GND (single ground star) |

## 2. Why these GPIOs

- All four are **safe-to-use** GPIOs on the ESP32-C3 (no strapping pin risk after boot).
- GPIO 2 is technically a strapping pin (tied to onboard LED on some boards). It still works for PWM output once boot completes, but if you ever need to enter download mode you may have to disconnect the CTRL line. GPIO 10 is the documented fallback.
- GPIOs 8, 9, 18–21 are reserved for onboard LED / USB / flash on the SuperMini — keep them untouched.

## 3. Wiring convention

For every CTRL connection:
```
ESP32 GPIO  ──[ 1 kΩ ]──┬── AL8860 CTRL
                        │
                     [100 kΩ]
                        │
                       GND
```
The 100 kΩ pull-down lives at the **first AL8860 CTRL pad**, not at the ESP32, so the line stays defined even if the ESP32 GPIO is high-Z during boot.

## 4. Firmware constants

These names match `pwm_test_sketch.ino`:
- `PIN_WHITE = 0`, `PIN_RED = 1`, `PIN_BLUE = 2`, `PIN_DEEPR = 3`
- `CH_WHITE/RED/BLUE/DEEPR = 0/1/2/3` (LEDC channels)
- `PWM_FREQ = 2000` Hz, `PWM_RES = 12` bits

If you swap a pin, change the `#define` in the `.ino` **and** the table here so they stay in sync.

## 5. Pin share note (white channel)

GPIO 0 drives all 4 white AL8860 CTRL inputs in parallel. Each AL8860's CTRL pin is high-impedance, so the four in parallel still draw only a few µA total — comfortably within ESP32-C3 GPIO drive (source/sink ±40 mA).

## 6. ESP32-C3 SuperMini pinout quick reference

```
                ┌─────────────────┐
        GND ────┤                 ├──── 5V (VBUS)
        GPIO 0 ─┤                 ├──── GPIO 1
        GPIO 2 ─┤                 ├──── GPIO 3
        GPIO 4 ─┤                 ├──── GPIO 5
        GPIO 6 ─┤                 ├──── GPIO 7
        GPIO 8 ─┤ (onboard LED)  ├──── GPIO 9 (strapping)
        GPIO10 ─┤                 ├──── GPIO 20
        GPIO21 ─┤                 ├──── GPIO 18
        GPIO19 ─┤                 ├──── GPIO 17
                └─────────────────┘
                       USB-C
```

Pins shown but **not used** by V0: 4, 5, 6, 7, 10, 17, 18, 19, 20, 21 (reserved for future use — V1 BLE/wifi, optional fan control, status LED).
