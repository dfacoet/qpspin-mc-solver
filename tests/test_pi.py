from collections.abc import Callable

import pytest

from qpspin_mc.pi import pi_mc_numpy, pi_mc_python, pi_mc_rust


@pytest.mark.parametrize("sampling_function", [pi_mc_numpy, pi_mc_python, pi_mc_rust])
def test_pi_mc(sampling_function: Callable[[int, int], float]) -> None:
    n_samples = 10
    result = sampling_function(n_samples, 0)
    assert result >= 0
    assert result <= 4.0 * n_samples


@pytest.mark.parametrize(
    ("n_samples", "seed"),
    [(0, 12345), (2**64, 12345), (10, 2**64), (-1, 12345), (10, -1)],
)
def test_pi_mc_rust_invalid(n_samples: int, seed: int) -> None:
    # TODO: make more precise
    with pytest.raises((ValueError, OverflowError)):
        pi_mc_rust(n_samples, seed)
