"""Tests for c_balance.py."""

import pytest

from c_balance import (
    AMMONIUM_PERCHLORATE,
    DEXTROSE,
    KNO3,
    SUCROSE,
    Compound,
    compound_oxygen_balance,
    elemental_mass_fractions,
    parse_formula,
    recipe_composition,
    recipe_oxygen_balance,
)


class TestParseFormula:
    def test_simple(self):
        assert parse_formula("KNO3") == {"K": 1, "N": 1, "O": 3}

    def test_multi_digit_subscripts(self):
        assert parse_formula("C12H22O11") == {"C": 12, "H": 22, "O": 11}

    def test_implicit_one_subscript(self):
        assert parse_formula("NH4ClO4") == {"N": 1, "H": 4, "Cl": 1, "O": 4}

    def test_single_element(self):
        assert parse_formula("Al") == {"Al": 1}

    def test_invalid_character_raises(self):
        with pytest.raises(ValueError, match="Unexpected character"):
            parse_formula("K-N-O")


class TestOxygenBalance:
    def test_KNO3_is_oxidizer(self):
        ob = compound_oxygen_balance(KNO3)
        # KNO3 has substantial excess oxygen
        assert ob > 35.0

    def test_sucrose_is_strongly_fuel_rich(self):
        ob = compound_oxygen_balance(SUCROSE)
        # Sucrose needs a lot of oxygen for complete combustion
        assert ob < -100.0

    def test_aluminum_is_fuel(self):
        ob = compound_oxygen_balance(ALUMINUM)
        assert ob < -100.0

    def test_AP_is_mildly_oxidizing(self):
        ob = compound_oxygen_balance(AMMONIUM_PERCHLORATE)
        assert 20.0 < ob < 40.0


class TestRecipeOxygenBalance:
    def test_KNSU_65_35_in_expected_range(self):
        # KNSU 65/35 is close to stoichiometric, expected OB around -8%
        components = [(KNO3, 0.65), (SUCROSE, 0.35)]
        ob = recipe_oxygen_balance(components)
        assert -12.0 < ob < -5.0

    def test_KNDX_65_35_in_expected_range(self):
        # KNDX is also near stoichiometric, slightly more negative
        components = [(KNO3, 0.65), (DEXTROSE, 0.35)]
        ob = recipe_oxygen_balance(components)
        assert -15.0 < ob < -5.0

    def test_normalizes_fractions_not_summing_to_one(self):
        components = [(KNO3, 0.66), (SUCROSE, 0.35)]  # sums to 1.01
        ob = recipe_oxygen_balance(components)
        assert -12.0 < ob < -5.0


class TestElementalMassFractions:
    def test_KNO3_sums_to_one(self):
        fractions = elemental_mass_fractions(KNO3)
        assert abs(sum(fractions.values()) - 1.0) < 1e-9

    def test_sucrose_sums_to_one(self):
        fractions = elemental_mass_fractions(SUCROSE)
        assert abs(sum(fractions.values()) - 1.0) < 1e-9

    def test_KNO3_contains_potassium(self):
        fractions = elemental_mass_fractions(KNO3)
        assert "K" in fractions
        assert fractions["K"] > 0.3  # K is ~39% of KNO3 by mass


class TestRecipeComposition:
    def test_KNSU_contains_expected_elements(self):
        composition = recipe_composition([(KNO3, 0.65), (SUCROSE, 0.35)])
        assert "K" in composition
        assert "N" in composition
        assert "C" in composition
        assert "H" in composition
        assert "O" in composition
        # Should sum to ~1.0
        assert abs(sum(composition.values()) - 1.0) < 1e-9
