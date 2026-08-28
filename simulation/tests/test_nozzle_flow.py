"""Tests for nozzle_flow.py."""

import math

import pytest

from nozzle_flow import (
    GasProperties,
    NozzleGeometry,
    analyze_nozzle,
    area_mach_ratio,
    chamber_to_stagnation_pressure,
    chamber_to_stagnation_temperature,
    critical_pressure_ratio,
    mach_from_area_ratio,
)
from physics import P_SEA_LEVEL


class TestIsentropicRelations:
    def test_critical_pressure_ratio_gamma_1_4(self):
        # Standard textbook value for gamma = 1.4
        assert math.isclose(critical_pressure_ratio(1.4), 0.5283, abs_tol=1e-3)

    def test_critical_pressure_ratio_gamma_1_22(self):
        # KNSU-like gamma should give a slightly different value
        ratio = critical_pressure_ratio(1.22)
        assert 0.55 < ratio < 0.58

    def test_area_mach_at_sonic(self):
        for gamma in [1.2, 1.3, 1.4, 1.67]:
            assert math.isclose(area_mach_ratio(1.0, gamma), 1.0, abs_tol=1e-6)

    def test_chamber_to_stagnation_at_zero_mach(self):
        assert math.isclose(
            chamber_to_stagnation_pressure(0.0, 1.4), 1.0, abs_tol=1e-6
        )
        assert math.isclose(
            chamber_to_stagnation_temperature(0.0, 1.4), 1.0, abs_tol=1e-6
        )

    def test_area_mach_inverse_round_trip(self):
        for m in [1.5, 2.0, 3.0, 5.0]:
            for gamma in [1.2, 1.3]:
                ar = area_mach_ratio(m, gamma)
                m_back = mach_from_area_ratio(ar, gamma, supersonic=True)
                assert math.isclose(m, m_back, abs_tol=1e-4)

    def test_mach_from_area_ratio_rejects_sub_unity(self):
        with pytest.raises(ValueError, match=">= 1.0"):
            mach_from_area_ratio(0.5, 1.3)

    def test_mach_from_area_ratio_returns_correct_branch(self):
        ar = 2.0
        gamma = 1.3
        m_sub = mach_from_area_ratio(ar, gamma, supersonic=False)
        m_sup = mach_from_area_ratio(ar, gamma, supersonic=True)
        assert 0.3 < m_sub < 1.0
        assert 1.0 < m_sup < 3.0


class TestNozzleAnalysis:
    def test_KNSU_like_motor_reasonable_sea_level_isp(self):
        gas = GasProperties(gamma=1.22, molecular_weight=35.0, chamber_temperature=1700.0)
        nozzle = NozzleGeometry(throat_area=1e-4, exit_area=2.5e-4)  # epsilon = 2.5
        result = analyze_nozzle(
            chamber_pressure=7e6,
            gas=gas,
            nozzle=nozzle,
            ambient_pressure=P_SEA_LEVEL,
        )
        # KNSU at sea level with moderate expansion should give 100-180 s
        assert 100.0 < result.isp_sea_level < 180.0
        assert result.is_choked
        assert result.exit_mach > 1.5

    def test_vacuum_isp_exceeds_sea_level_isp(self):
        gas = GasProperties(gamma=1.22, molecular_weight=35.0, chamber_temperature=1700.0)
        nozzle = NozzleGeometry(throat_area=1e-4, exit_area=4e-4)
        result = analyze_nozzle(
            chamber_pressure=7e6,
            gas=gas,
            nozzle=nozzle,
            ambient_pressure=0.0,
        )
        # KNSU-like motor at epsilon=4 in vacuum
        assert result.isp_vacuum > 140.0
        assert result.isp_vacuum > result.isp_sea_level

    def test_bisection_finds_correct_supersonic_mach(self):
        # Regression test: bisection previously returned the upper bound
        # (20.0) when the function value at midpoints was positive.
        for area_ratio in [1.5, 2.0, 3.0, 5.0, 10.0]:
            m = mach_from_area_ratio(area_ratio, gamma=1.22, supersonic=True)
            # Result should be in the physically meaningful range, not at boundary
            assert 1.0 < m < 6.0, (
                f"bisection failed for A/A*={area_ratio}: got M={m}"
            )
            # Verify inverse: area_mach_ratio(m) should round-trip
            assert math.isclose(
                area_mach_ratio(m, 1.22), area_ratio, rel_tol=1e-3
            )

    def test_unchoked_motor_zero_mass_flow(self):
        gas = GasProperties(gamma=1.4, molecular_weight=28.0, chamber_temperature=300.0)
        nozzle = NozzleGeometry(throat_area=1e-4, exit_area=2e-4)
        result = analyze_nozzle(
            chamber_pressure=P_SEA_LEVEL * 0.5,
            gas=gas,
            nozzle=nozzle,
            ambient_pressure=P_SEA_LEVEL,
        )
        assert not result.is_choked
        assert result.mass_flow_rate == 0.0

    def test_high_expansion_ratio_overexpanded_at_sea_level(self):
        # Large exit area relative to throat -> exit pressure below ambient
        gas = GasProperties(gamma=1.22, molecular_weight=35.0, chamber_temperature=1700.0)
        nozzle = NozzleGeometry(throat_area=1e-4, exit_area=10e-4)  # epsilon = 10
        result = analyze_nozzle(
            chamber_pressure=7e6,
            gas=gas,
            nozzle=nozzle,
            ambient_pressure=P_SEA_LEVEL,
        )
        # Epsilon = 10 at sea level is overexpanded
        assert result.is_overexpanded

    def test_mass_flow_scales_with_throat_area(self):
        gas = GasProperties(gamma=1.22, molecular_weight=35.0, chamber_temperature=1700.0)
        small = analyze_nozzle(
            chamber_pressure=7e6,
            gas=gas,
            nozzle=NozzleGeometry(throat_area=1e-4, exit_area=2e-4),
            ambient_pressure=P_SEA_LEVEL,
        )
        large = analyze_nozzle(
            chamber_pressure=7e6,
            gas=gas,
            nozzle=NozzleGeometry(throat_area=2e-4, exit_area=4e-4),
            ambient_pressure=P_SEA_LEVEL,
        )
        # Doubling throat area should double mass flow (everything else equal)
        assert math.isclose(large.mass_flow_rate / small.mass_flow_rate, 2.0, rel_tol=1e-3)
