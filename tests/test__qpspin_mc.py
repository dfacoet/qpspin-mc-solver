import pytest

from qpspin_mc._qpspin_mc import pi_exact_rust


def test_pi_exact_rust():
    assert pi_exact_rust() == pytest.approx(3.14159)
