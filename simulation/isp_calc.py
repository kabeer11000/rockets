"""Specific impulse calculation from static test thrust data.

Reads a thrust-time CSV (time_s, thrust_n) and computes:
    - Total impulse (integral of thrust over burn)
    - Burn time (first to last nonzero thrust)
    - Effective burn time (10% to 90% of total impulse)
    - Average thrust
    - Specific impulse (Isp = total_impulse / (propellant_mass * g0))

Integration uses the trapezoidal rule. Accuracy is limited by the sampling
rate of the input data — aim for >= 100 Hz sampling for fast burns.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from physics import G0


@dataclass(frozen=True)
class IspResult:
    """Result of Isp calculation."""
    total_impulse: float          # N*s
    average_thrust: float         # N
    burn_time: float              # s (first to last nonzero thrust)
    effective_burn_time: float    # s (10% to 90% of cumulative impulse)
    propellant_mass: float        # kg
    isp: float                    # s


def load_thrust_csv(path: str | Path) -> tuple[np.ndarray, np.ndarray]:
    """Load thrust CSV with time and thrust columns.

    Column names are matched case-insensitively. The time column must contain
    'time' and the thrust column must contain 'thrust'.

    Returns:
        (time_array, thrust_array) as 1D numpy arrays.

    Raises:
        ValueError: if the CSV has no header, no recognizable columns, or no
                    data rows.
    """
    path = Path(path)
    with path.open() as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"CSV {path} has no header")
        time_col = next((c for c in reader.fieldnames if "time" in c.lower()), None)
        thrust_col = next((c for c in reader.fieldnames if "thrust" in c.lower()), None)
        if time_col is None or thrust_col is None:
            raise ValueError(
                f"CSV {path} must have 'time' and 'thrust' columns, got {reader.fieldnames}"
            )
        rows = [(float(r[time_col]), float(r[thrust_col])) for r in reader]

    if not rows:
        raise ValueError(f"CSV {path} has no data rows")

    times, thrusts = zip(*rows)
    return np.array(times), np.array(thrusts)


def compute_isp(
    times: np.ndarray,
    thrusts: np.ndarray,
    propellant_mass: float,
) -> IspResult:
    """Compute Isp from thrust-time data and propellant mass.

    Args:
        times: time array (s), strictly monotonically increasing.
        thrusts: thrust array (N), same length as times.
        propellant_mass: total propellant mass (kg).

    Returns:
        IspResult with all metrics.

    Raises:
        ValueError: on invalid input shapes, monotonicity, or non-positive
                    propellant mass.
    """
    times = np.asarray(times, dtype=float)
    thrusts = np.asarray(thrusts, dtype=float)

    if times.shape != thrusts.shape:
        raise ValueError("times and thrusts must have the same shape")
    if times.size < 2:
        raise ValueError("need at least 2 data points for integration")
    if np.any(np.diff(times) <= 0):
        raise ValueError("times must be strictly monotonically increasing")
    if propellant_mass <= 0:
        raise ValueError(f"propellant_mass must be positive, got {propellant_mass}")

    # Total impulse via trapezoidal rule.
    total_impulse = float(np.trapz(thrusts, times))

    # Burn time: first to last nonzero thrust.
    nonzero = thrusts > 0
    if not np.any(nonzero):
        raise ValueError("no nonzero thrust values in data")
    first_idx = int(np.argmax(nonzero))
    last_idx = int(len(thrusts) - 1 - np.argmax(nonzero[::-1]))
    burn_time = float(times[last_idx] - times[first_idx])
    average_thrust = total_impulse / burn_time if burn_time > 0 else 0.0

    # Effective burn time: 10% to 90% of cumulative impulse.
    cumulative = np.concatenate([[0.0], np.cumsum(
        (thrusts[:-1] + thrusts[1:]) / 2.0 * np.diff(times)
    )])
    if total_impulse > 0:
        t10 = float(np.interp(0.10 * total_impulse, cumulative, times))
        t90 = float(np.interp(0.90 * total_impulse, cumulative, times))
        effective_burn_time = t90 - t10
    else:
        effective_burn_time = 0.0

    isp = total_impulse / (propellant_mass * G0)

    return IspResult(
        total_impulse=total_impulse,
        average_thrust=average_thrust,
        burn_time=burn_time,
        effective_burn_time=effective_burn_time,
        propellant_mass=propellant_mass,
        isp=isp,
    )
