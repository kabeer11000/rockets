"""Shared physical constants and unit conversions.

All quantities in SI unless noted. Conversion factors are explicit so callers
do not need to remember magic numbers.
"""

# --- Physical constants ---

# Standard gravity (m/s^2) — used for Isp calculation.
G0 = 9.80665

# Universal gas constant (J / (mol * K)).
R_UNIVERSAL = 8.314462618

# Atmospheric pressure at sea level, ISA (Pa).
P_SEA_LEVEL = 101_325.0

# --- Unit conversions ---

# Pressure
PA_PER_PSI = 6894.757293168
PA_PER_ATM = 101_325.0

# Length
M_PER_IN = 0.0254
M_PER_FT = 0.3048
M_PER_MM = 0.001

# Mass
KG_PER_LBM = 0.45359237
KG_PER_G = 0.001

# Force
N_PER_LBF = 4.4482216152605

# --- Common gas properties ---

# Specific heat ratio (gamma) for typical combustion products.
# These are approximate — real combustion products are mixtures and gamma
# varies with temperature.
GAMMA_DIATOMIC = 7.0 / 5.0          # N2, O2, H2 at moderate T (~1.40)
GAMMA_TRIATOMIC_LINEAR = 1.29       # CO2 at moderate T
GAMMA_WATER_VAPOR = 1.33            # H2O at moderate T

# Approximate gamma for KNSU combustion products (mostly N2, CO2, H2O, K2O).
# Nakka's experimental data suggests ~1.20-1.25 for typical KNSU formulations.
GAMMA_KNSU_APPROX = 1.22

# Molecular weight of air (g/mol) — used for sea-level Isp calculation.
MW_AIR = 28.97
