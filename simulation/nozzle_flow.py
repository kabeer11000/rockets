"""One-dimensional isentropic nozzle flow analysis.

Models choked, supersonic flow through a convergent-divergent nozzle using
standard isentropic relations. Assumes:
    - Steady-state flow
    - Calorically perfect gas (constant gamma)
    - No boundary layer losses
    - No shock waves inside the nozzle

Given chamber conditions (Pc, Tc, gamma, MW) and geometry (At, Ae), computes:
    - Mass flow rate
    - Exit Mach, pressure, temperature, velocity
    - Thrust (vacuum and sea-level)
    - Specific impulse (vacuum and sea-level)

References:
    Sutton, "Rocket Propulsion Elements", Ch. 3
    https://en.wikipedia.org/wiki/De_Laval_nozzle
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from physics import G0, R_UNIVERSAL


@dataclass(frozen=True)
class GasProperties:
    """Calorically perfect gas model.

    Attributes:
        gamma: ratio of specific heats (Cp/Cv), dimensionless.
        molecular_weight: g/mol.
        chamber_temperature: stagnation temperature K (assumed equal to chamber
                             T for an ideal gas with negligible combustion
                             delay).
    """
    gamma: float
    molecular_weight: float
    chamber_temperature: float


@dataclass(frozen=True)
class NozzleGeometry:
    """Nozzle dimensions.

    Attributes:
        throat_area: m^2.
        exit_area: m^2.
    """
    throat_area: float
    exit_area: float


@dataclass(frozen=True)
class NozzleResult:
    """Result of a nozzle flow analysis.

    All thrust and Isp values assume the nozzle is oriented along the thrust
    axis with mass flow exiting rearward. For sea-level Isp, the ambient
    pressure used in the calculation is included via the `ambient_pressure`
    input to analyze_nozzle (not stored here).
    """
    exit_mach: float
    exit_pressure: float           # Pa
    exit_temperature: float        # K
    exit_velocity: float           # m/s
    mass_flow_rate: float          # kg/s
    thrust_vacuum: float           # N
    thrust_sea_level: float        # N
    isp_vacuum: float              # s
    isp_sea_level: float           # s
    is_choked: bool                # throat flow is sonic
    is_underexpanded: bool         # Pe > Pa at exit (could expand more)
    is_overexpanded: bool          # Pe < Pa at exit (flow separates in diverging section)


# --- Isentropic flow relations ---


def critical_pressure_ratio(gamma: float) -> float:
    """P* / P0 at throat (sonic condition).

        P*/P0 = (2 / (gamma + 1)) ^ (gamma / (gamma - 1))

    For gamma = 1.4 this evaluates to ~0.5283.
    """
    return (2.0 / (gamma + 1.0)) ** (gamma / (gamma - 1.0))


def area_mach_ratio(mach: float, gamma: float) -> float:
    """A / A* as a function of Mach number.

        A/A* = (1/M) * [(2 / (gamma+1)) * (1 + (gamma-1)/2 * M^2)] ^ ((gamma+1) / (2*(gamma-1)))

    At M = 1, A/A* = 1 by definition.
    """
    if mach <= 0:
        raise ValueError(f"Mach must be positive, got {mach}")
    term = (2.0 / (gamma + 1.0)) * (1.0 + (gamma - 1.0) / 2.0 * mach * mach)
    exponent = (gamma + 1.0) / (2.0 * (gamma - 1.0))
    return (1.0 / mach) * term ** exponent


def mach_from_area_ratio(
    area_ratio: float,
    gamma: float,
    supersonic: bool = True,
) -> float:
    """Solve for Mach given A/A* and gamma.

    The area-Mach relation has two solutions: subsonic (M < 1) and supersonic
    (M > 1). For a converging-diverging nozzle, the diverging section is
    supersonic.

    Uses bisection on the area-Mach function. Iterative but guaranteed to
    converge for sensible inputs.

    Args:
        area_ratio: A / A*, must be >= 1.0.
        gamma: ratio of specific heats.
        supersonic: if True, return M > 1 solution; if False, return M < 1.

    Returns:
        Mach number.

    Raises:
        ValueError: if area_ratio < 1.0.
    """
    if area_ratio < 1.0:
        raise ValueError(f"area_ratio must be >= 1.0, got {area_ratio}")

    lo, hi = (1.0, 20.0) if supersonic else (0.01, 1.0)

    for _ in range(100):  # converges in ~50 iterations for typical inputs
        mid = (lo + hi) / 2.0
        f = area_mach_ratio(mid, gamma) - area_ratio
        if abs(f) < 1e-9:
            return mid
        # Area-Mach is monotonic in both branches (increasing supersonic,
        # decreasing subsonic), so the same sign rule works for both: f(mid)
        # sharing a sign with f(lo) means root lies in [mid, hi], and vice versa.
        if f > 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2.0


def chamber_to_stagnation_pressure(mach: float, gamma: float) -> float:
    """P0 / P at Mach (isentropic)."""
    return (1.0 + (gamma - 1.0) / 2.0 * mach * mach) ** (gamma / (gamma - 1.0))


def chamber_to_stagnation_temperature(mach: float, gamma: float) -> float:
    """T0 / T at Mach (isentropic)."""
    return 1.0 + (gamma - 1.0) / 2.0 * mach * mach


# --- Nozzle performance ---


def analyze_nozzle(
    chamber_pressure: float,
    gas: GasProperties,
    nozzle: NozzleGeometry,
    ambient_pressure: float,
) -> NozzleResult:
    """Analyze flow through a rocket nozzle.

    Args:
        chamber_pressure: stagnation pressure Pc (Pa).
        gas: gas properties (gamma, MW, chamber T).
        nozzle: throat and exit areas (m^2).
        ambient_pressure: back pressure Pa (Pa), e.g. 101325 for sea level.

    Returns:
        NozzleResult with all performance metrics.
    """
    gamma = gas.gamma
    mw_kg = gas.molecular_weight / 1000.0   # g/mol -> kg/mol
    r_specific = R_UNIVERSAL / mw_kg        # specific gas constant (J/(kg*K))
    t0 = gas.chamber_temperature

    # Critical (sonic) conditions at throat.
    p_star = critical_pressure_ratio(gamma)
    t_star = 2.0 / (gamma + 1.0)

    # Mass flow rate (choked flow at throat).
    # Derived from rho* = Pc*p_star / (R*T*), a* = sqrt(gamma*R*T*), m_dot = rho* * a* * At.
    # The (2/(gamma+1)) exponent in p_star and t_star combines algebraically into
    # (2/(gamma+1))^((gamma+1)/(2*(gamma-1))) — do not add it again.
    is_choked = chamber_pressure > ambient_pressure / p_star
    if is_choked:
        m_dot = (
            nozzle.throat_area
            * p_star * chamber_pressure
            * math.sqrt(gamma / (r_specific * t0 * t_star))
        )
    else:
        m_dot = 0.0

    # Exit Mach from area ratio.
    area_ratio = nozzle.exit_area / nozzle.throat_area
    if is_choked and area_ratio >= 1.0:
        exit_mach = mach_from_area_ratio(area_ratio, gamma, supersonic=True)
    elif is_choked:
        # Converging-only nozzle (Ae < At): subsonic exit.
        exit_mach = mach_from_area_ratio(area_ratio, gamma, supersonic=False)
    else:
        exit_mach = 0.0

    # Exit conditions.
    exit_pressure = chamber_pressure / chamber_to_stagnation_pressure(exit_mach, gamma)
    exit_temperature = t0 / chamber_to_stagnation_temperature(exit_mach, gamma)
    exit_velocity = exit_mach * math.sqrt(gamma * r_specific * exit_temperature)

    # Thrust (rocket equation: F = m_dot * Ve + (Pe - Pa) * Ae).
    thrust_vacuum = m_dot * exit_velocity + exit_pressure * nozzle.exit_area
    thrust_sea_level = (
        m_dot * exit_velocity
        + (exit_pressure - ambient_pressure) * nozzle.exit_area
    )

    # Isp.
    isp_vacuum = thrust_vacuum / (m_dot * G0) if m_dot > 0 else 0.0
    isp_sea_level = thrust_sea_level / (m_dot * G0) if m_dot > 0 else 0.0

    return NozzleResult(
        exit_mach=exit_mach,
        exit_pressure=exit_pressure,
        exit_temperature=exit_temperature,
        exit_velocity=exit_velocity,
        mass_flow_rate=m_dot,
        thrust_vacuum=thrust_vacuum,
        thrust_sea_level=thrust_sea_level,
        isp_vacuum=isp_vacuum,
        isp_sea_level=isp_sea_level,
        is_choked=is_choked,
        is_underexpanded=exit_pressure > ambient_pressure * 1.1,
        is_overexpanded=exit_pressure < ambient_pressure * 0.9,
    )
