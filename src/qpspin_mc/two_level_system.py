import math
from functools import cache, cached_property
from typing import Any, Literal

import numpy as np
from pydantic import BaseModel, Field

TwoLevelSystemSample = np.ndarray[Any, np.dtype[np.float64]]
# TODO: specify that the array is one-dimensional
# e.g. with np.ndarray[tuple[int], ...]
# but mypy does not understand this properly even with the plugin


NPSeedType = int | list[int]  # TODO: proper type of np random seed


class SystemParameters(BaseModel):
    beta: float = Field(gt=0, frozen=True)
    h: float = Field(frozen=True)
    gamma: float = Field(frozen=True)

    @cached_property
    def b(self) -> float:
        """Total magnetic field strength"""
        return np.sqrt(self.h**2 + self.gamma**2)

    def m(self) -> float:
        return self.gamma / self.b * math.tanh(self.beta * self.b)


class SimulationParameters(BaseModel):
    n_samples: int = Field(frozen=True)
    n_thinning: int = Field(frozen=True)
    n_init_steps: int = Field(frozen=True)
    seed: NPSeedType = Field(frozen=True)

    @property
    def n_steps(self) -> int:
        return self.n_samples * self.n_thinning


class SimulationResult(BaseModel):
    samples: list[TwoLevelSystemSample] = Field(frozen=True)
    accepted_steps: int = Field(frozen=True)

    system_parameters: SystemParameters = Field(frozen=True)
    simulation_parameters: SimulationParameters = Field(frozen=True)

    model_config = {"arbitrary_types_allowed": True}

    def acceptance_rate(self) -> float:
        return self.accepted_steps / (self.simulation_parameters.n_steps)

    def estimate_magnetization(self) -> tuple[float, float]:
        r = self.system_parameters.beta * self.system_parameters.gamma
        m_samples = [len(s) / r for s in self.samples]
        m_mean = float(np.mean(m_samples))
        m_sem = float(np.std(m_samples, ddof=1) / np.sqrt(len(m_samples)))
        return m_mean, m_sem


_P_ADD = 0.5  # Probability to propose "add"


class InvalidProposal(Exception):
    def __init__(self, state: Any, proposal: Any):
        super().__init__(f"Invalid proposal: {state} {proposal}")


class NoRNGError(Exception):
    def __init__(self):
        super().__init__("RNG not configured")


class TwoLevelSystemSimulator(BaseModel):
    """Continuous imaginary time Monte Carlo simulator for

    $$ H = - h * \\sigma_z - \\Gamma * \\sigma_x $$

    """

    system_parameters: SystemParameters = Field(frozen=True)

    _rng: np.random.Generator | None = None

    @property
    def beta(self) -> float:
        return self.system_parameters.beta

    @property
    def h(self) -> float:
        return self.system_parameters.h

    @property
    def gamma(self) -> float:
        return self.system_parameters.gamma

    def run_mc(self, simulation_parameters: SimulationParameters) -> SimulationResult:
        self._rng = np.random.default_rng(simulation_parameters.seed)

        samples = []
        accepted_steps = 0

        ts = self.initial()
        for _ in range(simulation_parameters.n_init_steps):
            ts, _ = self.step(ts)

        for _ in range(simulation_parameters.n_samples):
            for _ in range(simulation_parameters.n_thinning):
                ts, accepted = self.step(ts)
                accepted_steps += accepted
            samples.append(ts)

        self._rng = None
        return SimulationResult(
            samples=samples,
            accepted_steps=accepted_steps,
            system_parameters=self.system_parameters,
            simulation_parameters=simulation_parameters,
        )

    @property
    def rng(self) -> np.random.Generator:
        if self._rng is None:
            raise NoRNGError
        return self._rng

    # TODO: avoid recomputing weight for the same ts
    def weight(self, ts: TwoLevelSystemSample) -> float:
        s = _alternating_ones(len(ts)) @ ts
        return 2 * (self.gamma ** len(ts)) * math.cosh(self.h * (self.beta + 2 * s))

    def initial(self) -> TwoLevelSystemSample:
        return np.array([], dtype=np.float64)

    @staticmethod
    @cache
    def proposal_ratio(
        beta: float, two_l: int, add_or_remove: Literal["add", "remove"]
    ) -> float:
        match (two_l, add_or_remove):
            case (0, "add"):
                return beta**2 / 4
            case (2, "remove"):
                return 4 / beta**2
            case (_, "add"):
                return beta**2 / ((two_l + 2) * (two_l + 1))
            case (x, "remove") if x > 0:
                return two_l * (two_l - 1) / beta**2
            case _:
                raise InvalidProposal(two_l, add_or_remove)

    def step(
        self, ts: TwoLevelSystemSample
    ) -> tuple[TwoLevelSystemSample, Literal[0, 1]]:
        if len(ts) == 0 or self.rng.uniform() < _P_ADD:
            # Propose to add two flips
            two_ts = self.rng.uniform(low=0, high=self.beta, size=2)
            new_ts = np.sort(np.concatenate((ts, two_ts)))
            prop_ratio = self.proposal_ratio(self.beta, len(ts), "add")
        else:
            # Propose to remove two flips
            indices = self.rng.choice(len(ts), size=2, replace=False)
            new_ts = np.delete(ts, indices)
            prop_ratio = self.proposal_ratio(self.beta, len(ts), "remove")

        p = self.weight(new_ts) / self.weight(ts) * prop_ratio
        if self.rng.uniform() < p:
            return (new_ts, 1)  # accept
        else:
            return (ts, 0)  # reject


@cache
def _alternating_ones(n: int) -> np.ndarray[Any, np.dtype[np.float64]]:
    return np.tile([1.0, -1.0], n // 2)
