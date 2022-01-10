"""
# Monte Carlo Analysis

Creates stochastic processes for CELO price, validator adoption, and validator uptime processes,
sampled by run (for new seed) and timestep (for new sample),
and runs a Monte Carlo analysis of 5 runs.
"""

import copy

from model.types import Stage
import model.constants as constants
from model.stochastic_processes import create_stochastic_process_realizations
from experiments.default_experiment import experiment

# Make a copy of the default experiment to avoid mutation
experiment = copy.deepcopy(experiment)

# Change some simulation_configuration configuration settings
DELTA_TIME = 1  # epochs per timestep
SIMULATION_TIME_MONTHS = 24  # number of months
TIMESTEPS = constants.blocks_per_month * SIMULATION_TIME_MONTHS // DELTA_TIME

# Generate stochastic process realizations
MONTE_CARLO_RUNS = 5
celo_price_samples = create_stochastic_process_realizations("celo_price_samples", timesteps=TIMESTEPS, dt=DELTA_TIME, runs=MONTE_CARLO_RUNS)

parameter_overrides = {
    "stage": [Stage.Mento1],
    "celo_price_process": [lambda run, timestep: celo_price_samples[run - 1][timestep]],
}

experiment.simulations[0].runs = MONTE_CARLO_RUNS
experiment.simulations[0].timesteps = TIMESTEPS
# Override default experiment System Parameters
experiment.simulations[0].model.params.update(parameter_overrides)
