"""Tests for thrust_fit.py."""

import numpy as np
import pytest

from thrust_fit import fit_burn_rate_law, predict_burn_rate


class TestFitBurnRateLaw:
    def test_recovers_exact_coefficients(self):
        # Generate synthetic data from r = 5 * P^0.5
        a_true, n_true = 5.0, 0.5
        pressures = np.linspace(1.0, 10.0, 20)
        burn_rates = a_true * pressures ** n_true
        fit = fit_burn_rate_law(pressures, burn_rates)
        assert np.isclose(fit.a, a_true, rel_tol=1e-3)
        assert np.isclose(fit.n, n_true, abs_tol=1e-3)
        assert fit.r_squared > 0.9999

    def test_KNSU_like_fit_in_expected_range(self):
        # KNSU typical: a ~ 5 mm/s at 1 MPa reference, n ~ 0.45
        pressures = np.array([2.0, 4.0, 6.0, 8.0, 10.0])
        burn_rates = 5.5 * pressures ** 0.45
        fit = fit_burn_rate_law(pressures, burn_rates)
        assert 4.0 < fit.a < 7.0
        assert 0.35 < fit.n < 0.55

    def test_handles_noisy_data_gracefully(self):
        # Add 10% noise; fit should still be approximately correct
        rng = np.random.default_rng(42)
        pressures = np.linspace(1.0, 10.0, 30)
        burn_rates = 5.0 * pressures ** 0.5 * (1.0 + 0.05 * rng.standard_normal(30))
        fit = fit_burn_rate_law(pressures, burn_rates)
        assert np.isclose(fit.a, 5.0, rel_tol=0.1)
        assert np.isclose(fit.n, 0.5, abs_tol=0.05)

    def test_rejects_non_positive_pressure(self):
        with pytest.raises(ValueError, match="positive"):
            fit_burn_rate_law(np.array([0.0, 1.0]), np.array([1.0, 2.0]))

    def test_rejects_non_positive_burn_rate(self):
        with pytest.raises(ValueError, match="positive"):
            fit_burn_rate_law(np.array([1.0, 2.0]), np.array([0.0, 2.0]))

    def test_rejects_mismatched_shapes(self):
        with pytest.raises(ValueError, match="shape"):
            fit_burn_rate_law(np.array([1.0, 2.0]), np.array([1.0, 2.0, 3.0]))

    def test_rejects_empty_input(self):
        with pytest.raises(ValueError, match="empty"):
            fit_burn_rate_law(np.array([]), np.array([]))


class TestPredictBurnRate:
    def test_round_trip_with_fit(self):
        pressures = np.linspace(1.0, 10.0, 20)
        burn_rates = 4.0 * pressures ** 0.5
        fit = fit_burn_rate_law(pressures, burn_rates)
        predicted = predict_burn_rate(fit, 5.0)
        expected = 4.0 * 5.0 ** 0.5
        assert np.isclose(predicted, expected, rel_tol=1e-3)

    def test_predicts_zero_at_zero_pressure(self):
        fit = BurnRateLike(a=5.0, n=0.5)
        # Not actually zero because exponent is positive, but very small
        assert predict_burn_rate(fit, 0.0) == 0.0


# Helper for tests that don't need a real fit
from dataclasses import dataclass

@dataclass
class BurnRateLike:
    a: float
    n: float
