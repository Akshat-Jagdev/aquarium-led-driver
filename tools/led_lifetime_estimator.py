"""
AQUARIUM V0 LED LIGHT — LED LIFETIME ESTIMATOR
===============================================

Purpose:
  Estimate L70 / L50 lifetime of each LED channel based on junction
  temperature, drive current, and datasheet acceleration parameters.

  Uses a simplified Arrhenius-like model:
    temp_factor = exp(Ea/k * (1/T_ref - 1/T_use))     # > 1 when T_use > T_ref
  with Ea = 0.5 eV (typical for LED packages; LUXEON datasheets often
  use 0.4-0.6 eV).

  A hotter junction degrades the LED FASTER, so temp_factor must exceed 1
  when T_use > T_ref. (An earlier version of this script had the two
  temperatures reversed, which reported longer life at higher temperature.)

  Also computes a current-acceleration factor (square rule approximation):
    current_factor = (I_use / I_ref)^2

  Combined lifetime reduction:
    L_use = L_ref / (current_factor * temp_factor)

Usage:
  python tools/led_lifetime_estimator.py
"""

# ============================================================
#  USER INPUTS
# ============================================================

# Boltzmann constant in eV/K
KB_EV = 8.617333262e-5

# Activation energy (eV) — typical for LUXEON; tune from datasheet
ACTIVATION_ENERGY_EV = 0.5

# Reference conditions for the L70 projection.
# NOTE: Lumileds DS174 does NOT publish L70 for the LUXEON 5050 HE Plus
# (it refers to a separate reliability datasheet). T_REF_C and
# L70_REF_HOURS are therefore a NOMINAL reference used for RELATIVE
# comparison — replace them with confirmed Lumileds reliability data
# before quoting absolute lifetime figures.
T_REF_C = 85.0          # nominal reference junction/solder temp (deg C)
L70_REF_HOURS = 50000.0 # nominal L70 at the reference condition (h)

# Reference currents (mA) — datasheet test currents
I_REF_MA = {
    "White 5700K":    200.0,   # LUXEON 5050 HE Plus
    "Red 625nm":      120.0,   # LUXEON 2835 Red
    "Blue 448nm":     700.0,   # LUXEON Rubix (we under-drive)
    "Deep Red 660nm": 140.0,   # LUXEON SunPlus 2835
}

# Channel configuration (must match firmware + schematic)
CHANNELS = [
    # name,            I_use_mA,  Tj_est_C (from power_thermal_calculator.py)
    ("White 5700K",    250.0, 70.0),
    ("Red 625nm",      120.0, 65.0),
    ("Blue 448nm",     303.0, 72.0),
    ("Deep Red 660nm", 120.0, 65.0),
]

# ============================================================
#  CALCULATIONS
# ============================================================

def c_to_k(t_c):
    return t_c + 273.15

def arrhenius_factor(t_use_c, t_ref_c, ea_ev):
    """Returns the Arrhenius exponent used to build temp_factor = exp(...).

    Sign convention: running HOTTER than the reference (T_use > T_ref)
    must give a POSITIVE exponent so temp_factor > 1 (faster degradation,
    shorter life). The correct order is (1/T_ref - 1/T_use).
    """
    inv_use = 1.0 / c_to_k(t_use_c)
    inv_ref = 1.0 / c_to_k(t_ref_c)
    return (ea_ev / KB_EV) * (inv_ref - inv_use)

def main():
    print("=" * 72)
    print(" AQUARIUM V0 — LED LIFETIME ESTIMATE (L70)")
    print("=" * 72)
    print(f" Activation energy: {ACTIVATION_ENERGY_EV} eV")
    print(f" Reference Tj:      {T_REF_C} °C  ->  L70 nominal: {L70_REF_HOURS:,.0f} h")
    print()
    print(f"{'Channel':<18} {'I_use':>8} {'Tj_use':>8} {'I_fac':>7} "
          f"{'T_fac':>9} {'L70_h':>11} {'L70_yr':>9}")
    print("-" * 72)

    for name, i_use_ma, tj_use_c in CHANNELS:
        i_ref_ma = I_REF_MA[name]
        # Current acceleration (square law approximation)
        current_factor = (i_use_ma / i_ref_ma) ** 2
        # Temperature acceleration (Arrhenius)
        exp_arg = arrhenius_factor(tj_use_c, T_REF_C, ACTIVATION_ENERGY_EV)
        temp_factor = 2.718281828 ** exp_arg
        # Combined degradation multiplier
        rate_mult = current_factor * temp_factor
        # Lifetime at use conditions
        l70_hours = L70_REF_HOURS / rate_mult
        l70_years = l70_hours / (24 * 365)
        print(f"{name:<18} {i_use_ma:>6.0f}mA {tj_use_c:>6.1f}C "
              f"{current_factor:>6.2f}x {temp_factor:>8.2f}x "
              f"{l70_hours:>10,.0f} {l70_years:>8.1f}")

    print()
    print(" Notes")
    print("-" * 72)
    print(" - L70 = hours until LED output drops to 70% of initial.")
    print(" - L70_REF and T_REF are NOMINAL (placeholder) values for RELATIVE")
    print("   comparison. Lumileds DS174 does not publish L70 for the 5050; get")
    print("   official figures from the Lumileds reliability datasheet before")
    print("   quoting absolute lifetime.")
    print(" - I_fac is the square-law current acceleration (approximate).")
    print(" - T_fac is the Arrhenius temperature acceleration (hotter = shorter).")
    print(" - Tj_use should come from your measured heatsink temperature")
    print("   plus the LED theta_JC * P_LED estimate, OR from a thermocouple")
    print("   on the LED case during a thermal soak test (TP-04).")
    print(" - Activation energy 0.5 eV is a typical industry value; check")
    print("   LUXEON datasheets if a more specific number is available.")
    print()
    print(" Sanity target")
    print("-" * 72)
    print(" For a consumer aquarium light, aim for >= 30,000 h L70")
    print(" (~3.4 years continuous, or ~10 years at 8 h/day duty cycle).")
    print("=" * 72)

if __name__ == "__main__":
    main()
