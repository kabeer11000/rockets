"""Burn rate law fitting (Vieille's law).

The standard burn rate law for solid propellants is:

        r = a * P^n

where:
    r = burn rate (mm/s or in/s)
    P = chamber pressure (MPa or PSI)
    a = burn rate coefficient (depends on units)
    n = pressure exponent (typically 0.3 - 0.8)

In log-space this becomes a linear regression:

        log(r) = log(a) + n * log(P)

For KNSU at 65/35, typical values are a ~ 4-7 mm/s at 1 MPa reference and
n ~ 0.4-0.6. Values depend on grain density, casting method, and exact ratio.

References:
    Sutton, "Rocket Propulsion Elements", Ch. 4
    https://www.nakka-rocketry.net/burnrate.html
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from scipy.optimize import curve_fit


@dataclass(frozen=True)
class BurnRateFit:
    """Result of fitting r = a * P^n.

    Attributes:
        a: burn rate coefficient (units depend on input units).
        n: pressure exponent (dimensionless).
        a_stderr: standard error of a.
        n_stderr: standard error of n.
        r_squared: coefficient of determination (1 = perfect fit).
        pressure_range: (min, max) pressure in the input data.
    """
    a: float
    n: float
    a_stderr: float
    n_stderr: float
    r_squared: float
    pressure_range: tuple[float, float]


def _power_law(pressure: np.ndarray, a: float, n: float) -> np.ndarray:
    """r = a * P^n. Helper for scipy.optimize.curve_fit."""
    return a * np.power(pressure, n)


def fit_burn_rate_law(
    pressures: np.ndarray,
    burn_rates: np.ndarray,
) -> BurnRateFit:
    """Fit r = a * P^n to measurement pairs.

    Uses scipy.optimize.curve_fit with a log-space linear regression as the
    initial guess. Robust for noisy data and small sample sizes.

    Args:
        pressures: chamber pressure measurements (1D array). Units determine
                   the units of `a` in the output — keep them consistent with
                   the burn_rates input.
        burn_rates: corresponding burn rate measurements (1D array).

    Returns:
        BurnRateFit with fitted coefficients and statistics.

    Raises:
        ValueError: if inputs are empty, contain non-positive values, or have
                    mismatched lengths.
    """
    pressures = np.asarray(pressures, dtype=float)
    burn_rates = np.asarray(burn_rates, dtype=float)

    if pressures.shape != burn_rates.shape:
        raise ValueError("pressures and burn_rates must have the same shape")
    if pressures.size == 0:
        raise ValueError("input arrays must not be empty")
    if np.any(pressures <= 0) or np.any(burn_rates <= 0):
        raise ValueError("all pressures and burn_rates must be positive")

    # Initial guess from log-space linear regression.
    log_p = np.log(pressures)
    log_r = np.log(burn_rates)
    n_guess, log_a_guess = np.polyfit(log_p, log_r, 1)
    p0 = [math.exp(log_a_guess), n_guess]

    popt, pcov = curve_fit(
        _power_law, pressures, burn_rates, p0=p0, maxfev=10000
    )
    a, n = popt
    a_stderr, n_stderr = np.sqrt(np.diag(pcov))

    # R-squared.
    predicted = _power_law(pressures, a, n)
    ss_res = float(np.sum((burn_rates - predicted) ** 2))
    ss_tot = float(np.sum((burn_rates - np.mean(burn_rates)) ** 2))
    r_squared = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0

    return BurnRateFit(
        a=a,
        n=n,
        a_stderr=a_stderr,
        n_stderr=n_stderr,
        r_squared=r_squared,
        pressure_range=(float(np.min(pressures)), float(np.max(pressures))),
    )


def predict_burn_rate(fit: BurnRateFit, pressure: float) -> float:
    """Predict burn rate at a given pressure using the fitted law."""
    return fit.a * pressure ** fit.n
