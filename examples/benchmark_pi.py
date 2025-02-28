import timeit
from collections.abc import Callable

import numpy as np

from qpspin_mc.pi import estimate_error, pi_mc_numpy, pi_mc_python


def benchmark_function(func: Callable, n_samples: int, seed: int, n_iter: int) -> float:
    """Run benchmark for a given function.

    Args:
        func: Function to benchmark
        n_samples: Number of samples for Monte Carlo
        seed: Random seed
        number: Number of times to run the benchmark

    Returns:
        Average execution time in seconds
    """
    return timeit.timeit(lambda: func(n_samples, seed), number=n_iter) / n_iter


def main():
    # Test different sample sizes
    sample_sizes = [10**i for i in range(3, 8)]
    seed = 55185189319

    print("Benchmarking Monte Carlo Pi estimation methods:")
    print("\n n_samples | Python | NumPy | Speedup")
    print("-" * 50)

    for n_samples in sample_sizes:
        n_iter = max(1, 1_000_000 // n_samples)

        time_python = benchmark_function(pi_mc_python, n_samples, seed, n_iter)
        time_numpy = benchmark_function(pi_mc_numpy, n_samples, seed, n_iter)

        speedup = time_python / time_numpy

        print(
            f"{n_samples:10d} | {time_python:9.6f} |"
            f" {time_numpy:9.6f} | {speedup:7.2f}x"
        )

    # TODO: formatting, significant digits etc
    print(f"\nPi approximation verification (using {sample_sizes[-1]} samples):")
    for impl, f in [("Python", pi_mc_python), ("NumPy ", pi_mc_numpy)]:
        estimate = f(sample_sizes[-1], seed)
        print(
            f"{impl}: {estimate:.6f}±{estimate_error(estimate, sample_sizes[-1]):.6f}"
        )
    print(f"Actual: {np.pi:.6f}")


if __name__ == "__main__":
    main()
