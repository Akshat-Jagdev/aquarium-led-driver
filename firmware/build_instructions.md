# ESP32-C3 Firmware — Build & Upload

> How to compile and flash `pwm_test_sketch.ino` to the ESP32-C3 SuperMini
> used in the V0 aquarium light.

## 1. What you need

- ESP32-C3 SuperMini (USB-C)
- USB-C cable (data + power, not charge-only)
- A computer with Arduino IDE 2.x **or** PlatformIO
- The V0 schematic already wired so GPIO 0/1/2/3 each have a 1 kΩ → CTRL
  and a 100 kΩ → GND

## 2. Arduino IDE setup (recommended for V0)

### 2.1 Install ESP32 board support
1. Open Arduino IDE 2.x.
2. Go to **File → Preferences** (Arduino IDE → Settings on macOS).
3. In **Additional boards manager URLs**, paste:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. Click OK. Open **Tools → Board → Boards Manager**, search **esp32**,
   install **esp32 by Espressif Systems** (v2.0.14 or newer).

### 2.2 Board settings
- **Tools → Board → ESP32 → ESP32C3 Dev Module**
- **USB CDC On Boot**: Enabled
- **CPU Frequency**: 160 MHz
- **Flash Mode**: QIO
- **Flash Size**: 4MB (32Mb)
- **Port**: the COM port your SuperMini enumerates on (Windows) or
  `/dev/cu.usbmodem*` (macOS), `/dev/ttyACM0` (Linux)

### 2.3 Open the sketch
1. **File → Open** → navigate to `firmware/pwm_test_sketch.ino`.
2. Verify the pin defines at the top of the file match
   `firmware/esp32_pin_map.md`.
3. Click **Upload**.

### 2.4 First-time USB note
On Windows, the SuperMini usually enumerates as a USB CDC device without a
driver. If it shows as "Unknown device", install the **CH343** or **CP210x**
driver depending on which clone you bought. Most modern SuperMini boards
use the on-board **ESP32-C3 native USB** and need no driver.

## 3. PlatformIO setup (alternative)

Create `firmware/platformio.ini` next to the sketch with:

```ini
[env:esp32c3-supermini]
platform = espressif32
board = esp32-c3-devkitm-1
framework = arduino
monitor_speed = 115200
upload_speed = 921600
build_flags =
    -DCORE_DEBUG_LEVEL=3
```

Then:
```bash
cd firmware
pio run -t upload
pio device monitor
```

## 4. Verifying the upload

After upload, open the serial monitor at **115200 baud**. You should see:

```
Aquarium V0 LED Controller
Commands: 0-3 select profile, +/- adjust, p=print
```

If you see only garbage, double-check baud rate (115200) and that the
USB cable is a data cable.

## 5. Serial command reference

| Key | Action |
|-----|--------|
| `0` | Profile A: white only |
| `1` | Profile B: white + red |
| `2` | Profile C: white + red + blue |
| `3` | Profile D: all channels |
| `n` | Next profile |
| `p` | Print current profile |
| `o` | All channels off |

Profiles are defined in `pwm_test_sketch.ino` (`profiles[]`). Edit the duty
values there to change brightness.

## 6. Troubleshooting

| Symptom | Likely cause |
|---------|-------------|
| No serial output | Wrong baud rate, or charge-only USB cable |
| Upload fails "no serial data" | Hold BOOT button while plugging USB, release after 1 s |
| LEDs flicker visibly | PWM frequency too low — check `PWM_FREQ = 2000` |
| LEDs flash at boot | Pull-down R missing on the affected CTRL line |
| One channel stays on at full brightness | 100 kΩ pull-down missing or CTRL shorted high |
| All channels on at boot | 1 kΩ series resistor open (CTRL floating) |

## 7. After successful upload

Run **TP-01 (one-channel bench test)** first — apply 24 V to a single
AL8860 channel on perfboard, then confirm the firmware drives it through
the GPIO → 1 kΩ → CTRL path. Move to the full PCB only after TP-01 passes.
