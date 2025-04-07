def tls_test_function(input_list: list[float]) -> tuple[set[int], float | None]: ...
def run_mc(
    gamma: float,
    h: float,
    beta: float,
    n_init_steps: int,
    n_samples: int,
    n_thinning: int,
    seed: int,
) -> tuple[list[float], int]: ...
