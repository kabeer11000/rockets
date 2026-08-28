"""Tests for isp_calc.py."""

import math

import numpy as np
import pytest

from isp_calc import compute_isp, load_thrust_csv
from physics import G0


class TestLoadThrustCsv:
    def test_loads_basic_csv(self, tmp_path):
        p = tmp_path / "thrust.csv"
        p.write_text("time_s,thrust_n\n0.0,0\n1.0,100\n2.0,0\n")
        times, thrusts = load_thrust_csv(p)
        assert np.array_equal(times, [0.0, 1.0, 2.0])
        assert np.array_equal(thrusts, [0.0, 100.0, 0.0])

    def test_loads_with_alternate_column_names(self, tmp_path):
        p = tmp_path / "thrust.csv"
        p.write_text("Time (s),Thrust (N)\n0.0,0\n1.0,100\n")
        times, thrusts = load_thrust_csv(p)
        assert len(times) == 2
        assert len(thrusts) == 2

    def test_rejects_csv_without_time_column(self, tmp_path):
        p = tmp_path / "bad.csv"
        p.write_text("foo,bar\n0,0\n")
        with pytest.raises(ValueError, match="time"):
            load_thrust_csv(p)

    def test_rejects_empty_data(self, tmp_path):
        p = tmp_path / "empty.csv"
        p.write_text("time_s,thrust_n\n")
        with pytest.raises(ValueError, match="no data"):
            load_thrust_csv(p)


class TestComputeIsp:
    def test_constant_thrust(self):
        # 100 N for 2 seconds, 1 kg propellant
        # Total impulse = 200 N*s, Isp = 200 / (1 * g0)
        times = np.array([0.0, 1.0, 2.0])
        thrusts = np.array([100.0, 100.0, 100.0])
        result = compute_isp(times, thrusts, propellant_mass=1.0)
        assert math.isclose(result.total_impulse, 200.0, rel_tol=1e-6)
        assert math.isclose(result.isp, 200.0 / G0, rel_tol=1e-6)

    def test_triangular_thrust_curve(self):
        # Triangle: 0 -> 100 -> 0 over 2 seconds, area = 100 N*s
        times = np.array([0.0, 1.0, 2.0])
        thrusts = np.array([0.0, 100.0, 0.0])
        result = compute_isp(times, thrusts, propellant_mass=1.0)
        assert math.isclose(result.total_impulse, 100.0, rel_tol=1e-3)

    def test_rejects_non_monotonic_time(self):
        times = np.array([0.0, 1.0, 0.5])
        thrusts = np.array([0.0, 100.0, 50.0])
        with pytest.raises(ValueError, match="monotonically"):
            compute_isp(times, thrusts, propellant_mass=1.0)

    def test_rejects_zero_mass(self):
        times = np.array([0.0, 1.0])
        thrusts = np.array([100.0, 100.0])
        with pytest.raises(ValueError, match="positive"):
            compute_isp(times, thrusts, propellant_mass=0.0)

    def test_rejects_mismatched_shapes(self):
        times = np.array([0.0, 1.0])
        thrusts = np.array([0.0, 100.0, 0.0])
        with pytest.raises(ValueError, match="shape"):
            compute_isp(times, thrusts, propellant_mass=1.0)

    def test_effective_burn_time_within_full_duration(self):
        times = np.linspace(0, 3, 31)
        thrusts = np.concatenate([np.linspace(0, 100, 16), np.linspace(100, 0, 15)])
        result = compute_isp(times, thrusts, propellant_mass=1.0)
        assert result.effective_burn_time < result.burn_time
        assert result.effective_burn_time > 0.0

    def test_rejects_data_with_no_thrust(self):
        times = np.array([0.0, 1.0, 2.0])
        thrusts = np.array([0.0, 0.0, 0.0])
        with pytest.raises(ValueError, match="no nonzero thrust"):
            compute_isp(times, thrusts, propellant_mass=1.0)

    def test_rejects_too_few_points(self):
        times = np.array([0.0])
        thrusts = np.array([100.0])
        with pytest.raises(ValueError, match="2 data points"):
            compute_isp(times, thrusts, propellant_mass=1.0)
