/*
 * AQUARIUM V0 — Production LED Controller
 * ===============================================
 *
 * This firmware implements the final channel mapping and PWM control
 * for the V0 prototype. It includes a default "Daylight" mode for
 * boot-up and a Serial interface for profile switching.
 *
 * Target: ESP32-C3 SuperMini
 * Framework: Arduino ESP32
 *
 * Hardware Mapping:
 *   GPIO 0 -> White Channel (4x AL8860)
 *   GPIO 1 -> Red Channel (1x AL8860)
 *   GPIO 2 -> Blue Channel (1x AL8860)
 *   GPIO 3 -> Deep Red Channel (1x AL8860)
 *
 * PWM Specs: 2 kHz, 12-bit (0-4095)
 */

#include <Arduino.h>

// Pin definitions
#define PIN_WHITE  0
#define PIN_RED    1
#define PIN_BLUE   2
#define PIN_DEEPR  3

// PWM settings
#define PWM_FREQ     2000
#define PWM_RES      12

// LEDC channel assignments
#define CH_WHITE  0
#define CH_RED    1
#define CH_BLUE   2
#define CH_DEEPR  3

struct Profile {
  const char* name;
  uint16_t white;
  uint16_t red;
  uint16_t blue;
  uint16_t deepR;
};

// Defined Profiles based on Visual Benchmarking
Profile profiles[] = {
  {"Daylight (Default)", 3000, 1000,  500,  300},
  {"White Only",         3500,    0,    0,    0},
  {"Color Boost (Red)",  3000, 2000,    0,    0},
  {"Tropical Glow",      2500, 1500, 1000,  500},
  {"Night Mode",           500,    0,  800,    0},
  {"All Off",                0,    0,    0,    0},
};

const int NUM_PROFILES = sizeof(profiles) / sizeof(profiles[0]);
int currentProfileIdx = 0;

void applyProfile(int idx) {
  if (idx < 0 || idx >= NUM_PROFILES) return;

  Profile p = profiles[idx];
  ledcWrite(CH_WHITE, p.white);
  ledcWrite(CH_RED,   p.red);
  ledcWrite(CH_BLUE,  p.blue);
  ledcWrite(CH_DEEPR, p.deepR);

  Serial.printf("Applied Profile: %s [W:%u R:%u B:%u DR:%u]\\n",
                p.name, p.white, p.red, p.blue, p.deepR);
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("========================================");
  Serial.println("   AQUARIUM V0 LED CONTROLLER SYSTEM    ");
  Serial.println("========================================");

  // Configure PWM channels
  ledcSetup(CH_WHITE, PWM_FREQ, PWM_RES);
  ledcSetup(CH_RED,   PWM_FREQ, PWM_RES);
  ledcSetup(CH_BLUE,  PWM_FREQ, PWM_RES);
  ledcSetup(CH_DEEPR, PWM_FREQ, PWM_RES);

  ledcAttachPin(PIN_WHITE, CH_WHITE);
  ledcAttachPin(PIN_RED,   CH_RED);
  ledcAttachPin(PIN_BLUE,  CH_BLUE);
  ledcAttachPin(PIN_DEEPR, CH_DEEPR);

  // Start with the default Daylight profile
  applyProfile(0);

  Serial.println("System Ready. Commands:");
  Serial.println("  0-5 : Select Profile");
  Serial.println("  n   : Next Profile");
  Serial.println("  p   : Print current status");
  Serial.println("  o   : All Off");
  Serial.println("----------------------------------------");
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();

    if (c >= '0' && c <= '5') {
      currentProfileIdx = c - '0';
      applyProfile(currentProfileIdx);
    } else if (c == 'n') {
      currentProfileIdx = (currentProfileIdx + 1) % NUM_PROFILES;
      applyProfile(currentProfileIdx);
    } else if (c == 'p') {
      Serial.println("Current Status:");
      applyProfile(currentProfileIdx);
    } else if (c == 'o') {
      applyProfile(5); // "All Off"
      currentProfileIdx = 5;
    }
  }
}
