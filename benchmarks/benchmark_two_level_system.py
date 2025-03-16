# from typing import ClassVar

# from qpspin_mc.two_level_system import (
#     SimulationParameters,
#     SystemParameters,
#     TwoLevelSystemSimulator,
# )


# class TwoLevelSystemBenchmark:
#     param_names: ClassVar[list[str]] = ["n_samples"]

#     params = ([10**i for i in range(1, 7)],)

#     def setup(self):
#         system_parameters = SystemParameters(beta=1.0, h=1.0, gamma=1.0)
#         self.simulator = TwoLevelSystemSimulator(system_parameters)

#     def time_run_mc(self, n_samples):
#         simulation_parameters = SimulationParameters(
#             n_samples=n_samples,
#             n_thinning=10,
#             n_init_steps=100,
#             seed=55181876890,
#         )
#         self.simulator.run_mc(simulation_parameters)
