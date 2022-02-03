"""
Default simulation_configuration configuration such as the number of timesteps and Monte Carlo runs
"""

from model.constants import blocks_per_day, blocks_per_month, blocks_per_year

# TODO this naming convention is quite missleading
DELTA_TIME = 1  # number of blocks per timestep (=1 if sim on per-block-basis)
SIMULATION_TIME_DAYS = 1  # number of days
# number of simulation_configuration timesteps
TIMESTEPS = SIMULATION_TIME_DAYS * blocks_per_day // DELTA_TIME
TIMESTEPS_PER_YEAR = blocks_per_year // DELTA_TIME
MONTE_CARLO_RUNS = 2  # number of run
