"""
AQUARIUM V0 LED LIGHT — POWER & THERMAL CALCULATOR
====================================================

Purpose:
  Verify your LED driver design BEFORE ordering PCBs.
  Calculates per-channel power, total power, AL8860 dissipation,
  and estimates LED junction temperature from expected heatsink temp.

Usage:
  1. Install Python 3.x (free from python.org)
  2. Open a terminal in the folder containing this file
  3. Run: python power_thermal_calculator.py

You can edit the parameters in the CHANNELS list below to match your
LED configuration. The script will print a summary and warn you if
any limits are exceeded.
"""

# ============================================================
#  USER INPUTS — edit these for your design
# ============================================================

# Each channel: (name, num_leds, vf_per_led, current_amps, count_of_strings)
CHANNELS = [
    ("White 5700K",   3, 5.85, 0.250, 4),   # LUXEON 5050 HE Plus
    ("Red 625nm",     4, 2.10, 0.120, 1),   # LUXEON 2835 Red
    ("Blue 448nm",    2, 3.16, 0.303, 1),   # LUXEON Rubix
    ("Deep Red 660nm",2, 2.15, 0.120, 1),   # LUXEON SunPlus 660
]

VIN = 24.0  # Supply voltage (from Mean Well LRS-35-24)
AL8860_RDSON = 0.4   # ohms, internal switch Rds(on)
DIODE_VF = 0.45       # volts, Schottky forward drop (SS3100 at operating current)
DRIVER_EFF_LOSS = 0.10  # additional fixed losses per channel (gate drive, etc.) in W

# Thermal estimates (you must measure these for accuracy)
EXPECTED_HEATSINK_TEMP_C = 50.0  # estimated steady-state heatsink temp
AMBIENT_TEMP_C = 30.0            # typical aquarium room temp

# LED thermal resistance (junction to case, K/W) — from datasheets
LED_THETA_JC = {
    "White 5700K":   1.5,   # LUXEON 5050 HE Plus (estimate from datasheet)
    "Red 625nm":     6.0,   # LUXEON 2835 (estimate)
    "Blue 448nm":    2.0,   # LUXEON Rubix
    "Deep Red 660nm":6.0,   # LUXEON SunPlus 2835
}

# LED thermal resistance (junction to board, with MCPCB)
LED_THETA_JB = 3.0  # K/W (typical for MCPCB with thermal pad)

# ============================================================
#  CALCULATIONS — do not edit
# ============================================================

def fmt(x, digits=2):
    return f"{x:.{digits}f}"

def main():
    print("="*68)
    print(" AQUARIUM V0 LED DRIVER — POWER & THERMAL ANALYSIS")
    print("="*68)
    print(f" Supply voltage: {VIN} V")
    print(f" AL8860 Rds(on): {AL8860_RDSON} Ω")
    print(f" Diode Vf:       {DIODE_VF} V")
    print()
    print(f"{'Channel':<18} {'Vf_str':>8} {'I_A':>7} {'P_str':>8} {'D':>6} {'I_in':>7} {'P_in':>7} {'P_loss':>7} {'#':>3} {'P_tot':>7}")
    print("-"*100)

    total_input_w = 0.0
    total_output_w = 0.0
    total_loss_w = 0.0
    channel_powers = {}

    for name, n_leds, vf, i, count in CHANNELS:
        vf_str = vf * n_leds
        p_str = vf_str * i
        d = vf_str / VIN
        i_in = i * d
        p_in = VIN * i_in
        # Loss = V_in*I_in - V_led*I_led
        p_loss = p_in - p_str
        # Per driver IC dissipation (switch + diode)
        p_switch = (i**2) * AL8860_RDSON * d
        p_diode = DIODE_VF * i * (1 - d)
        p_driver = p_switch + p_diode + DRIVER_EFF_LOSS
        # Total for this channel type
        p_total = p_str * count
        p_total_in = p_in * count

        total_input_w += p_total_in
        total_output_w += p_total
        total_loss_w += (p_total_in - p_total)
        channel_powers[name] = {
            "p_str": p_str,
            "count": count,
            "p_total": p_total,
            "vf_str": vf_str,
            "i": i,
            "n_leds": n_leds,
        }

        print(f"{name:<18} {fmt(vf_str,2):>6}V {fmt(i,3):>7} {fmt(p_str,2):>6}W {fmt(d,3):>6} {fmt(i_in,3):>7} {fmt(p_in,2):>5}W {fmt(p_loss,2):>5}W {count:>3} {fmt(p_total,2):>5}W")

    print("-"*100)
    print(f"{'TOTAL':<18} {'':>8} {'':>7} {fmt(total_output_w,2):>6}W {'':>6} {'':>7} {fmt(total_input_w,2):>5}W {fmt(total_loss_w,2):>5}W {'':>3} {fmt(total_output_w,2):>5}W")
    print()
    print(f" PSU current at full load: {fmt(total_input_w/VIN,3)} A")
    print(f" Mean Well LRS-35-24 rating: 1.5 A -> margin: {fmt((1.5*VIN - total_input_w)/VIN,2)} A spare")
    print()

    # Warnings
    print("="*68)
    print(" WARNINGS / CHECKS")
    print("="*68)

    psu_ok = total_input_w < (1.5 * VIN)
    print(f" [{'OK' if psu_ok else 'FAIL'}] PSU capacity: {fmt(total_input_w,1)} W < {1.5*VIN} W (LRS-35-24)")

    for name, info in channel_powers.items():
        i = info["i"]
        vf_str = info["vf_str"]
        # RSET calculation
        rset = 0.1 / i
        p_in_rset = (i**2) * rset
        print(f" [{name}] RSET = {fmt(rset,3)} Ω  -> use standard {fmt(round(rset,2),2)} Ω  (P_dissipation: {fmt(p_in_rset*1000,1)} mW)")

        # AL8860 dissipation estimate
        d = vf_str / VIN
        p_switch = (i**2) * AL8860_RDSON * d
        p_diode = DIODE_VF * i * (1 - d)
        p_driver = p_switch + p_diode + DRIVER_EFF_LOSS
        print(f"   AL8860 dissipation: {fmt(p_driver*1000,1)} mW per IC")

    # LED junction temperature estimate
    print()
    print("="*68)
    print(" LED JUNCTION TEMPERATURE (estimate, must verify with measurement)")
    print("="*68)
    print(f" Assumed heatsink temp: {EXPECTED_HEATSINK_TEMP_C}°C")
    print(f" Assumed ambient:      {AMBIENT_TEMP_C}°C")
    print()
    for name, info in channel_powers.items():
        p_str = info["p_str"]
        vf_str = info["vf_str"]
        i = info["i"]
        n_leds = info["n_leds"]
        theta_jc = LED_THETA_JC.get(name, 2.0)
        # Junction temp = heatsink + P_led * (theta_jc + theta_jb)
        p_per_led = p_str / n_leds  # W per LED
        tj = EXPECTED_HEATSINK_TEMP_C + p_per_led * (theta_jc + LED_THETA_JB)
        status = "OK" if tj < 85 else ("WARN" if tj < 110 else "FAIL")
        print(f" [{status}] {name}: Tj ≈ {fmt(tj,1)}°C (limit 85°C for L50 lifetime)")
        if tj > 85:
            print(f"         -> REDUCE current OR improve heatsink")
    print()
    print("="*68)


if __name__ == "__main__":
    main()
