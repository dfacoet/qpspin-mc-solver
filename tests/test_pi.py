from collections.abc import Callable

import pytest

from qpspin_mc.pi import pi_mc_numpy, pi_mc_python, pi_mc_rust


@pytest.mark.parametrize("sampling_function", [pi_mc_numpy, pi_mc_python, pi_mc_rust])
def test_pi_mc(sampling_function: Callable[[int, int], float]) -> None:
    n_samples = 10
    result = sampling_function(n_samples, 0)
    assert result >= 0
    assert result <= 4.0 * n_samples
