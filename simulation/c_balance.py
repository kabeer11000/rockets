"""Oxygen balance and elemental composition of propellant recipes.

Oxygen balance (OB) is the mass of oxygen (per 100 g of propellant) released by
or required for complete combustion to CO2 and H2O. Zero is stoichiometric.

    Positive OB = excess oxygen (oxidizer-rich)
    Negative OB = fuel-rich

For rocket propellants, OB near zero or slightly negative (typically 0 to
-15%) gives the best performance — too oxidizer-rich leaves excess O2 in
the exhaust (low Isp); too fuel-rich leaves CO and soot (also low Isp).

References:
    Kubota, N. "Propellant Chemistry"
    https://en.wikipedia.org/wiki/Oxygen_balance
"""

from __future__ import annotations

from dataclasses import dataclass


# Atomic masses (g/mol), IUPAC 2021 standard atomic weights.
ATOMIC_MASS = {
    "H": 1.008,
    "Li": 6.94,
    "Be": 9.0122,
    "B": 10.81,
    "C": 12.011,
    "N": 14.007,
    "O": 15.999,
    "F": 18.998,
    "Na": 22.990,
    "Mg": 24.305,
    "Al": 26.982,
    "Si": 28.085,
    "P": 30.974,
    "S": 32.06,
    "Cl": 35.45,
    "K": 39.098,
    "Ca": 40.078,
    "Fe": 55.845,
}


@dataclass(frozen=True)
class Compound:
    """A chemical compound with formula and molecular weight.

    Attributes:
        name: Human-readable identifier.
        formula: Hill-system formula. Carbon first, hydrogen second, others
                 alphabetical. Subscripts are digits; parentheses are not
                 supported by the parser in this module.
        molecular_weight: g/mol.
    """
    name: str
    formula: str
    molecular_weight: float


# Common propellant ingredients. Molecular weights verified against NIST.
KNO3 = Compound(name="potassium nitrate", formula="KNO3", molecular_weight=101.103)
SUCROSE = Compound(name="sucrose", formula="C12H22O11", molecular_weight=342.30)
DEXTROSE = Compound(name="dextrose (glucose)", formula="C6H12O6", molecular_weight=180.156)
AMMONIUM_PERCHLORATE = Compound(name="ammonium perchlorate", formula="NH4ClO4", molecular_weight=117.49)
AMMONIUM_NITRATE = Compound(name="ammonium nitrate", formula="NH4NO3", molecular_weight=80.043)
ALUMINUM = Compound(name="aluminum", formula="Al", molecular_weight=26.982)
HTPB_APPROX = Compound(name="HTPB (approximate C10H16)", formula="C10H16", molecular_weight=136.23)


def parse_formula(formula: str) -> dict[str, int]:
    """Parse a Hill-system formula into element counts.

    Examples:
        >>> parse_formula("KNO3")
        {'K': 1, 'N': 1, 'O': 3}
        >>> parse_formula("C12H22O11")
        {'C': 12, 'H': 22, 'O': 11}
        >>> parse_formula("NH4ClO4")
        {'N': 1, 'H': 4, 'Cl': 1, 'O': 4}
    """
    atoms: dict[str, int] = {}
    i = 0
    while i < len(formula):
        if not formula[i].isalpha():
            raise ValueError(f"Unexpected character at position {i}: {formula[i]!r}")
        symbol = formula[i]
        i += 1
        while i < len(formula) and formula[i].islower():
            symbol += formula[i]
            i += 1
        subscript = ""
        while i < len(formula) and formula[i].isdigit():
            subscript += formula[i]
            i += 1
        count = int(subscript) if subscript else 1
        atoms[symbol] = atoms.get(symbol, 0) + count
    return atoms


def elemental_mass_fractions(compound: Compound) -> dict[str, float]:
    """Mass fraction of each element in a compound.

    Returns dict mapping element symbol to mass fraction (sums to 1.0).
    """
    atoms = parse_formula(compound.formula)
    masses = {sym: ATOMIC_MASS[sym] * count for sym, count in atoms.items()}
    total = sum(masses.values())
    return {sym: m / total for sym, m in masses.items()}


def compound_oxygen_balance(compound: Compound) -> float:
    """Oxygen balance of a single compound (% by mass).

    OB = -1600 * (2*C + H/2 - O) / MW
    where C, H, O are atom counts.

    Returns:
        OB as percentage of compound mass.
        Positive = excess oxygen (oxidizer).
        Negative = requires oxygen to combust (fuel).
    """
    atoms = parse_formula(compound.formula)
    c = atoms.get("C", 0)
    h = atoms.get("H", 0)
    o = atoms.get("O", 0)
    return -1600.0 * (2 * c + h / 2 - o) / compound.molecular_weight


def recipe_composition(
    components: list[tuple[Compound, float]],
) -> dict[str, float]:
    """Elemental mass fractions of a propellant recipe.

    Args:
        components: list of (compound, mass_fraction) pairs. Mass fractions
                    should sum to 1.0 (within floating-point tolerance).

    Returns:
        Dict mapping element symbol to total mass fraction in recipe.
    """
    total: dict[str, float] = {}
    for compound, fraction in components:
        for sym, mass_frac in elemental_mass_fractions(compound).items():
            total[sym] = total.get(sym, 0.0) + mass_frac * fraction

    s = sum(total.values())
    if s > 0:
        total = {k: v / s for k, v in total.items()}
    return total


def recipe_oxygen_balance(components: list[tuple[Compound, float]]) -> float:
    """Oxygen balance of a propellant recipe (% by mass of total propellant).

    For KNSU at 65/35 KNO3/sucrose, expected OB is approximately -8%.
    Near-zero or slightly negative OB is typical for optimal rocket
    propellants.

    Args:
        components: list of (compound, mass_fraction) pairs.

    Returns:
        OB as percent of total propellant mass.
    """
    total_ob = 0.0
    for compound, fraction in components:
        total_ob += compound_oxygen_balance(compound) * fraction
    return total_ob
