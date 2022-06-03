"""
Default simulation_configuration configuration such as the number of timesteps and Monte Carlo runs
"""
from model.constants import blocks_per_day, blocks_per_year

BLOCKS_PER_TIMESTEP = 1  # number of blocks per timestep (=1 if sim on per-block-basis)
SIMULATION_TIME_DAYS = 1  # number of days
# number of simulation_configuration timesteps
TIMESTEPS = SIMULATION_TIME_DAYS * blocks_per_day // BLOCKS_PER_TIMESTEP
TIMESTEPS_PER_YEAR = blocks_per_year // BLOCKS_PER_TIMESTEP
MONTE_CARLO_RUNS = 1  # number of runs
DATA_SOURCE = 'historical'   # 'mock' or 'historical'
TOTAL_BLOCKS = (BLOCKS_PER_TIMESTEP * TIMESTEPS) + 1
