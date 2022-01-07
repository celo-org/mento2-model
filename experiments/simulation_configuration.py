"""
Default simulation configuration such as the number of timesteps and Monte Carlo runs
"""

from model.constants import blocks_per_day


DELTA_TIME = 1  # blocks per timestep (sim on per block basis)
SIMULATION_TIME_DAYS = 365  # number of days
TIMESTEPS = (
    SIMULATION_TIME_DAYS * blocks_per_day // DELTA_TIME
)  # number of simulation timesteps
MONTE_CARLO_RUNS = 1  # number of runs
