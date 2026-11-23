"""
AQUARIUM V0 LED LIGHT — PWM FREQUENCY ANALYZER
===============================================

Purpose:
  Helps you pick a PWM frequency that is:
    1. Above fish flicker detection threshold (typically 100-200 Hz)
    2. Below audible coil whine (~20 kHz upper bound for most people)
    3. Within AL8860 capability (max 20 kHz per datasheet)
    4. A frequency where the LEDC peripheral on ESP32-C3 gives clean resolution

  It also estimates the PWM frequency that will actually appear at the LED
  given the AL8860 CTRL pin RC time constant (1 kohm series + CTRL pin
  capacitance + 100 kohm pull-down).

Usage:
  python tools/pwm_freq_analyzer.py
"""

# ============================================================
#  USER INPUTS — edit if you change the design
# ============================================================

FISH_FLICKER_MIN_HZ = 200.0   # conservative; some species go higher
HUMAN_HEARING_MAX_HZ = 20000.0 # above this is inaudible to most adults
AL8860_CTRL_MAX_HZ   = 20000.0 # from datasheet
ESP32_LEDC_MAX_HZ    = 40000000.0 # hardware limit, not a real constraint here

# Current chosen frequency (must match firmware PWM_FREQ in pwm_test_sketch.ino)
CURRENT_PWM_FREQ_HZ  = 2000.0
CURRENT_PWM_RES_BITS = 12

# AL8860 CTRL pin interface
SERIES_RES_OHMS       = 1000.0   # 1 kohm between ESP32 GPIO and CTRL
PULLDOWN_RES_OHMS     = 100000.0 # 100 kohm CTRL to GND
CTRL_PIN_CAP_PF       = 10.0     # AL8860 CTRL pin capacitance (estimate)
ESP32_GPIO_CAP_PF     = 5.0      # ESP32 GPIO + trace

# ============================================================
#  ANALYSIS
# ============================================================

def fmt(x, digits=2):
    return f"{x:.{digits}f}"

def main():
    print("=" * 68)
    print(" AQUARIUM V0 — PWM FREQUENCY ANALYSIS")
    print("=" * 68)
    print()
    print(" Design constraints")
    print("-" * 68)
    print(f" Fish flicker lower bound       : {FISH_FLICKER_MIN_HZ:>10.0f} Hz")
    print(f" AL8860 CTRL max PWM frequency  : {AL8860_CTRL_MAX_HZ:>10.0f} Hz")
    print(f" Human audible (coil whine) lim : {HUMAN_HEARING_MAX_HZ:>10.0f} Hz")
    print()
    print(" Current selection")
    print("-" * 68)
    print(f" PWM frequency                  : {CURRENT_PWM_FREQ_HZ:>10.0f} Hz")
    print(f" PWM resolution                 : {CURRENT_PWM_RES_BITS:>10d} bits")
    print(f" PWM period                     : {1e6/CURRENT_PWM_FREQ_HZ:>10.2f} us")
    print(f" Min pulse width (1 LSB)        : "
          f"{1e6/(CURRENT_PWM_FREQ_HZ * (2**CURRENT_PWM_RES_BITS)):>10.3f} us")
    print(f" Duty resolution                : "
          f"{100.0/(2**CURRENT_PWM_RES_BITS):>10.4f} % per step")
    print()

    # Frequency band checks
    print(" Frequency checks")
    print("-" * 68)
    checks = [
        (CURRENT_PWM_FREQ_HZ > FISH_FLICKER_MIN_HZ,
         f"Above fish flicker ({FISH_FLICKER_MIN_HZ:.0f} Hz)",
         "PASS", "FAIL"),
        (CURRENT_PWM_FREQ_HZ < AL8860_CTRL_MAX_HZ,
         f"Within AL8860 capability ({AL8860_CTRL_MAX_HZ:.0f} Hz)",
         "PASS", "FAIL"),
        (CURRENT_PWM_FREQ_HZ < HUMAN_HEARING_MAX_HZ,
         f"Below human hearing ({HUMAN_HEARING_MAX_HZ:.0f} Hz) — no coil whine",
         "PASS", "WARN"),
    ]
    for ok, desc, p, f in checks:
        tag = p if ok else f
        print(f"  [{tag}] {desc}")
    print()

    # RC time constant at CTRL pin
    # Thevenin equivalent seen by CTRL pin capacitance:
    #   R_th = (R_series || R_pulldown)  when GPIO drives a square wave
    # For a high-low transition, the relevant R is the series R (charging
    # through 1k) and the pulldown (100k) is a discharge path. Worst-case
    # time constant is dominated by 1 kohm charging the pin capacitance.
    print(" CTRL pin RC analysis")
    print("-" * 68)
    c_total_pf = CTRL_PIN_CAP_PF + ESP32_GPIO_CAP_PF
    # Charge path (GPIO high -> CTRL high) is through 1 k series resistor
    tau_charge_us = SERIES_RES_OHMS * c_total_pf * 1e-6  # R * C in us when C is pF and R is ohm
    # Discharge path is via 100 k pulldown (plus GPIO low impedance ~30 ohm)
    r_discharge = PULLDOWN_RES_OHMS
    tau_discharge_us = r_discharge * c_total_pf * 1e-6
    print(f" Total CTRL-node capacitance   : {c_total_pf:>10.1f} pF")
    print(f" Charge time constant (1k path): {tau_charge_us:>10.3f} us")
    print(f" Discharge time const (100k)   : {tau_discharge_us:>10.3f} us")
    period_us = 1e6 / CURRENT_PWM_FREQ_HZ
    half_us = period_us / 2.0
    print(f" PWM half-period at {CURRENT_PWM_FREQ_HZ:.0f} Hz      : {half_us:>10.2f} us")
    charge_ok = tau_charge_us * 5 < half_us  # 5 tau to settle
    print(f"  [{'PASS' if charge_ok else 'FAIL'}] CTRL pin settles within half-period")
    print()

    # ESP32 LEDC clock considerations
    print(" ESP32-C3 LEDC clock notes")
    print("-" * 68)
    # ESP32-C3 LEDC peripheral: source clock 80 MHz APB, divider 1..8192
    # freq = 80e6 / (divider * (1 << bits))
    src_clk = 80e6
    print(f" LEDC source clock             : {src_clk/1e6:>10.0f} MHz")
    print(f" Required divider              : "
          f"{src_clk / (CURRENT_PWM_FREQ_HZ * (2**CURRENT_PWM_RES_BITS)):>10.2f}")
    print(f"   (must be an integer >= 1 and <= 8192)")
    # Pick a divider that fits
    needed = src_clk / (CURRENT_PWM_FREQ_HZ * (2**CURRENT_PWM_RES_BITS))
    chosen_div = max(1, round(needed))
    actual_freq = src_clk / (chosen_div * (2**CURRENT_PWM_RES_BITS))
    print(f" Actual achievable frequency   : {actual_freq:>10.1f} Hz")
    print(f" Frequency error               : "
          f"{100.0*(actual_freq - CURRENT_PWM_FREQ_HZ)/CURRENT_PWM_FREQ_HZ:>+10.3f} %")
    print()

    # Recommendations
    print(" Recommendations")
    print("-" * 68)
    if 1000 <= CURRENT_PWM_FREQ_HZ <= 5000:
        print(" Current selection is in the recommended band (1-5 kHz).")
        print(" - Above fish flicker detection with comfortable margin")
        print(" - Far enough below 20 kHz to avoid audible coil whine")
        print(" - Low enough that switching loss on AL8860 is negligible")
        print(" - ESP32 LEDC achieves it cleanly at 12-bit resolution")
    elif CURRENT_PWM_FREQ_HZ < FISH_FLICKER_MIN_HZ:
        print(f" WARNING: PWM frequency is below fish flicker threshold!")
        print(f" Raise PWM_FREQ to >= {FISH_FLICKER_MIN_HZ:.0f} Hz (recommended 2000 Hz).")
    elif CURRENT_PWM_FREQ_HZ > HUMAN_HEARING_MAX_HZ:
        print(" PWM is above human hearing; OK, but 2 kHz is sufficient and")
        print(" slightly reduces switching loss.")
    print()
    print("=" * 68)

if __name__ == "__main__":
    main()
