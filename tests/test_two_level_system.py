import math

import numpy as np
import pytest
from pydantic import ValidationError

from qpspin_mc.two_level_system import (
    InvalidProposal,
    NoRNGError,
    SimulationParameters,
    SimulationResult,
    SystemParameters,
    TwoLevelSystemSimulator,
    _alternating_ones,
    tls_function,
)


class TestSystemParameters:
    def test_validate_beta(self):
        # beta must be positive
        with pytest.raises(ValueError, match="Input should be greater than 0"):
            SystemParameters(beta=-1.0, h=1.0, gamma=1.0)

    def test_b_property(self):
        params = SystemParameters(beta=1.0, h=3.0, gamma=4.0)
        assert params.b == 5.0

    @pytest.mark.parametrize(
        ("beta", "h", "gamma", "expected"),
        [
            (1.0, 0.0, 1.0, math.tanh(1.0)),  # pure transverse field
            (1.0, 1.0, 0.0, 0.0),  # pure longitudinal field
        ],
    )
    def test_m_property(self, beta, h, gamma, expected):
        params = SystemParameters(beta=beta, h=h, gamma=gamma)
        assert params.m() == expected


class TestSimulationParameters:
    def test_frozen_fields(self):
        params = SimulationParameters(
            n_samples=10, n_thinning=10, n_init_steps=10, seed=42
        )
        with pytest.raises(ValidationError):
            params.n_thinning = 200

    def test_n_steps_property(self):
        params = SimulationParameters(
            n_samples=10, n_thinning=5, n_init_steps=10, seed=42
        )
        assert params.n_steps == 50  # n_samples * n_thinning


class TestSimulationResult:
    @pytest.fixture
    def system_params(self):
        return SystemParameters(beta=1.0, h=1.0, gamma=1.0)

    @pytest.fixture
    def sim_params(self):
        return SimulationParameters(
            n_samples=9, n_thinning=11, n_init_steps=10, seed=42
        )

    @pytest.fixture
    def result(self, system_params, sim_params):
        return SimulationResult(
            samples=[np.array([0.1, 0.2]), np.array([0.3, 0.4])],
            accepted_steps=50,
            system_parameters=system_params,
            simulation_parameters=sim_params,
        )

    def test_acceptance_rate(self, result):
        assert result.acceptance_rate() == 50 / 99

    def test_estimate_magnetization(self, result):
        m_mean, m_sem = result.estimate_magnetization()
        assert isinstance(m_mean, float)
        assert isinstance(m_sem, float)


class TestTwoLevelSystemSimulator:
    @pytest.fixture
    def system_params(self):
        return SystemParameters(beta=1.0, h=1.0, gamma=1.0)

    @pytest.fixture(
        params=[  # n_samples, n_thinning, n_init_steps
            (10, 10, 100),
            (6, 86, 10),
            (100, 10, 100),
        ],
    )
    def sim_params(self, request):
        n_samples, n_thinning, n_init_steps = request.param
        return SimulationParameters(
            n_samples=n_samples,
            n_thinning=n_thinning,
            n_init_steps=n_init_steps,
            seed=42,
        )

    @pytest.fixture
    def simulator(self, system_params):
        return TwoLevelSystemSimulator(system_parameters=system_params)

    def test_initial_state(self, simulator):
        ts = simulator.initial()
        assert len(ts) == 0
        assert ts.dtype == np.float64

    def test_proposal_ratio(self, simulator):
        assert simulator.proposal_ratio(1.0, 0, "add") == 0.25
        assert simulator.proposal_ratio(1.0, 2, "remove") == 4.0

        # Invalid proposals should raise
        with pytest.raises(InvalidProposal):
            simulator.proposal_ratio(1.0, 0, "remove")

    def test_weight(self, simulator):
        ts = np.array([0.1, 0.2, 0.3, 0.4], dtype=np.float64)
        w = simulator.weight(ts)
        assert isinstance(w, float)
        assert w > 0

    def test_run_mc(self, simulator, sim_params):
        result = simulator.run_mc(sim_params)
        assert isinstance(result, SimulationResult)
        assert len(result.samples) == sim_params.n_samples

    def test_rng_not_configured(self, simulator):
        with pytest.raises(NoRNGError):
            _ = simulator.rng

    def test_step(self, simulator):
        simulator._rng = np.random.default_rng()  # noqa: SLF001
        ts = simulator.initial()
        new_ts, accepted = simulator.step(ts)
        assert isinstance(new_ts, np.ndarray)
        assert accepted in (0, 1)


def test_alternating_ones():
    ones = _alternating_ones(4)
    np.testing.assert_array_equal(ones, [1.0, -1.0, 1.0, -1.0])

    # Test caching
    assert _alternating_ones(4) is _alternating_ones(4)


@pytest.mark.parametrize(
    ("input_list", "expected_set", "expected_maybe_float"),
    [
        ([], set(), None),
        ([11.0], set(), 11.0),
        ([0.0, 1.0, 2.0], {0, 1, 2, 3}, None),
        ([0.0, 10.0, 2.0], {0, 1, 2, 3}, 12.0),
        ([7.0, 2.0, 3.0], {1, 2, 3, 7}, 12.0),
        ([-10.0, 2.0, 3.0], {1, 2, 3, 0}, None),
    ],
)
def test_tls_function(
    input_list: list[float], expected_set: set[int], expected_maybe_float: float | None
):
    assert tls_function(input_list) == (expected_set, expected_maybe_float)


@pytest.mark.parametrize(
    ("input_list", "expected_err"),
    [
        (["invalid_type", 1.0], TypeError),
    ],
)
def test_tls_function_error(input_list: list[float], expected_err: type[BaseException]):
    with pytest.raises(expected_err):
        tls_function(input_list)
