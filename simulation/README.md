# Simulation

Trajectory simulation, thermochemistry, and analysis tools.

## Trajectory simulation

**OpenRocket** — open-source Java app for airframe and flight simulation.
- Models rocket aerodynamics, fin flutter, recovery deployment
- Imports standard motor thrust curves
- Free: https://openrocket.info/

## Thermochemistry

**Rocket Propulsion Analysis (RPA)** — free limited edition for amateurs.
- Calculates theoretical Isp, chamber conditions, nozzle flow
- Has a library of propellants and combustion products
- Free: https://www.rocketpropulsionanalysis.com/

## Python toolkit

Lives in this directory:

| Module | Purpose |
|---|---|
| `physics.py` | Shared constants (g0, R_universal) and unit conversions |
| `c_balance.py` | Oxygen balance and elemental composition of recipes |
| `nozzle_flow.py` | 1D isentropic nozzle analysis with Isp calculation |
| `isp_calc.py` | Specific impulse from static test thrust CSV |
| `thrust_fit.py` | Burn rate law (r = a * P^n) fitting from measurements |

## Setup

```sh
cd simulation
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS / Linux
pip install -r requirements.txt
```

## Running the tests

```sh
pytest simulation/tests -v
```

## Usage examples

### Oxygen balance for a KNSU recipe

```python
from c_balance import KNO3, SUCROSE, recipe_oxygen_balance

ob = recipe_oxygen_balance([(KNO3, 0.65), (SUCROSE, 0.35)])
print(f"KNSU 65/35 oxygen balance: {ob:.1f}%")
# Expected: ~-28%
```

### Theoretical Isp from a nozzle analysis

```python
from nozzle_flow import GasProperties, NozzleGeometry, analyze_nozzle
from physics import P_SEA_LEVEL

gas = GasProperties(gamma=1.22, molecular_weight=35.0, chamber_temperature=1700.0)
nozzle = NozzleGeometry(throat_area=1e-4, exit_area=2.5e-4)

result = analyze_nozzle(
    chamber_pressure=7e6,    # 7 MPa
    gas=gas,
    nozzle=nozzle,
    ambient_pressure=P_SEA_LEVEL,
)

print(f"Sea-level Isp: {result.isp_sea_level:.1f} s")
print(f"Vacuum Isp:    {result.isp_vacuum:.1f} s")
print(f"Exit Mach:     {result.exit_mach:.2f}")
```

### Isp from a static test CSV

```python
from isp_calc import load_thrust_csv, compute_isp

times, thrusts = load_thrust_csv("static-tests/test-001/thrust.csv")
result = compute_isp(times, thrusts, propellant_mass=0.050)  # 50 g

print(f"Total impulse: {result.total_impulse:.1f} N*s")
print(f"Burn time:     {result.burn_time:.2f} s")
print(f"Isp:           {result.isp:.1f} s")
```

### Burn rate law from measurements

```python
import numpy as np
from thrust_fit import fit_burn_rate_law, predict_burn_rate

# Suppose we measured (pressure_MPa, burn_rate_mm_per_s) pairs
pressures = np.array([2.0, 4.0, 6.0, 8.0])
burn_rates = np.array([7.2, 9.8, 11.7, 13.2])

fit = fit_burn_rate_law(pressures, burn_rates)
print(f"a = {fit.a:.2f} mm/s, n = {fit.n:.3f}, R^2 = {fit.r_squared:.4f}")

# Predict burn rate at any pressure
print(f"r at 5 MPa: {predict_burn_rate(fit, 5.0):.2f} mm/s")
```

## Validation

Always validate simulation against measured data. The first KNSU static test
should produce results within 10-15% of theoretical. Larger discrepancies
point to:
- Grain geometry not as designed (voids, uneven casting)
- Nozzle throat erosion
- Heat losses (especially for short burns)
- Measurement errors

## TODO

- [ ] Add a plotting module (`plots.py`) using matplotlib for thrust curves,
      pressure traces, and nozzle exit conditions
- [ ] Add a `burn_time.py` module for estimating burn time from grain geometry
      and burn rate law
- [ ] Add a grain regression simulator for BATES and star grains
