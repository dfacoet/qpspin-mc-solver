import math
import random

import numpy as np

from ._qpspin_mc import pi

# re-export pi_mc_rust. `from ._qpspin_mc.pi import pi_mc_rust` does not work
# because _qpspin_mc is not a package.
# See extended comment in rust/lib.rs
pi_mc_rust = pi.pi_mc_rust


def pi_mc_python(n_samples: int, seed: int) -> float:
    random.seed(seed)
    n_in = sum(
        random.random() ** 2 + random.random() ** 2 < 1 for _ in range(n_samples)
    )
    return 4 * n_in / n_samples


def pi_mc_numpy(n_samples: int, seed: int) -> float:
    rng = np.random.default_rng(seed)
    # generating all samples at once is more efficient,
    # but might use too much memory for large n_samples
    samples = rng.random(size=(n_samples, 2))
    n_in = (samples**2).sum(axis=1) < 1
    return 4 * n_in.sum() / n_samples


def estimate_error(estimate: float, n_samples: int) -> float:
    # estimate is 4/N * n where n~B(n_samples, pi/4)
    # so the standard error can be computed without estimating
    # the variance separately
    var = estimate * (4 - estimate) / n_samples
    return math.sqrt(var)
