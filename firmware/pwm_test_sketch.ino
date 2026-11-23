/*
 * AQUARIUM V0 — ESP32-C3 PWM Control Test Sketch
 * ===============================================
 *
 * This sketch controls 4 LED channels via PWM.
 * Designed for ESP32-C3 SuperMini using Arduino framework.
 *
 * Connections:
 *   GPIO 0 -> 1kΩ -> CTRL of all 4 white AL8860s
 *   GPIO 1 -> 1kΩ -> CTRL of red AL8860
 *   GPIO 2 -> 1kΩ -> CTRL of blue AL8860
 *   GPIO 3 -> 1kΩ -> CTRL of deep red AL8860
 *
 *   Each CTRL pin also has 100kΩ to GND (pull-down).
 *
 * Install via Arduino IDE:
 *   1. Add ESP32 board URL: https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
 *   2. Install "esp32" board package (v2.0.14+)
 *   3. Select board: ESP32C3 Dev Module
 *   4. Select USB CDC On Boot: Enabled
 *   5. Upload
 */

// Pin definitions
#define PIN_WHITE  0
#define PIN_RED    1
#define PIN_BLUE   2
#define PIN_DEEPR  3

// PWM settings
#define PWM_FREQ     2000   // 2 kHz — avoids visible flicker
#define PWM_RES      12     // 12-bit resolution (0–4095)

// LEDC channel assignments
#define CH_WHITE  0
#define CH_RED    1
#define CH_BLUE   2
#define CH_DEEPR  3

// Preset profiles
struct Profile {
  const char* name;
  uint16_t white;
  uint16_t red;
  uint16_t blue;
  uint16_t deepR;
};

Profile profiles[] = {
  {"A: White only",      3500,    0,    0,    0},
  {"B: White + Red",     3500, 1500,    0,    0},
  {"C: W+R+Blue",        3000, 1500,  800,    0},
  {"D: All channels",    3000, 1500,  800,  600},
};

const int NUM_PROFILES = sizeof(profiles) / sizeof(profiles[0]);
int currentProfile = 0;

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("Aquarium V0 LED Controller");
  Serial.println("Commands: 0-3 select profile, +/- adjust, p=print");

  // Configure PWM channels
  ledcSetup(CH_WHITE, PWM_FREQ, PWM_RES);
  ledcSetup(CH_RED,   PWM_FREQ, PWM_RES);
  ledcSetup(CH_BLUE,  PWM_FREQ, PWM_RES);
  ledcSetup(CH_DEEPR, PWM_FREQ, PWM_RES);

  ledcAttachPin(PIN_WHITE, CH_WHITE);
  ledcAttachPin(PIN_RED,   CH_RED);
  ledcAttachPin(PIN_BLUE,  CH_BLUE);
  ledcAttachPin(PIN_DEEPR, CH_DEEPR);

  // Start with all off
  applyProfile(0);
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    if (c >= '0' && c <= '3') {
      currentProfile = c - '0';
      applyProfile(currentProfile);
    } else if (c == 'n') {
      currentProfile = (currentProfile + 1) % NUM_PROFILES;
      applyProfile(currentProfile);
    } else if (c == 'p') {
      printProfile(currentProfile);
    } else if (c == 'w' || c == 'r' || c == 'b' || c == 'd') {
      // Manual adjustment
      adjustChannel(c);
    } else if (c == 'o') {
      // All off
      ledcWrite(CH_WHITE, 0);
      ledcWrite(CH_RED, 0);
      ledcWrite(CH_BLUE, 0);
      ledcWrite(CH_DEEPR, 0);
      Serial.println("All channels OFF");
    }
  }
}

void applyProfile(int idx) {
  if (idx < 0 || idx >= NUM_PROFILES) return;
  Profile* p = &profiles[idx];
  ledcWrite(CH_WHITE, p->white);
  ledcWrite(CH_RED,   p->red);
  ledcWrite(CH_BLUE,  p->blue);
  ledcWrite(CH_DEEPR, p->deepR);
  printProfile(idx);
}

void printProfile(int idx) {
  if (idx < 0 || idx >= NUM_PROFILES) return;
  Profile* p = &profiles[idx];
  Serial.printf("[%s] W=%4u R=%4u B=%4u DR=%4u\n",
    p->name, p->white, p->red, p->blue, p->deepR);
}

void adjustChannel(char ch) {
  // Simple up/down via serial — full version would parse numbers
  // For V0, just print help
  Serial.println("Manual mode: use profiles 0-3 for now");
}
