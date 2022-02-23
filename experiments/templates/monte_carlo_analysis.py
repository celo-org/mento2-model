"""
# Monte Carlo Analysis

Creates stochastic processes for CELO price, validator adoption, and validator uptime processes,
sampled by run (for new seed) and timestep (for new sample),
and runs a Monte Carlo analysis of 5 runs.
"""

import copy

import model.constants as constants
from model.stochastic_processes import create_stochastic_process_realizations
from experiments.default_experiment import experiment

# Make a copy of the default experiment to avoid mutation
experiment = copy.deepcopy(experiment)

# Change some simulation_configuration configuration settings
BLOCKS_PER_TIMESTEP = 1  # blocks per timestep
TIMESTEPS = constants.blocks_per_year * 3 // BLOCKS_PER_TIMESTEP

# Generate stochastic process realizations
MONTE_CARLO_RUNS = 5
cusd_demand_samples = create_stochastic_process_realizations(
    "cusd_demand_process", timesteps=TIMESTEPS, dt=BLOCKS_PER_TIMESTEP, runs=MONTE_CARLO_RUNS
)

parameter_overrides = {
    "cusd_demand": [lambda run, timestep: cusd_demand_samples[run - 1][timestep]],
}

experiment.simulations[0].runs = MONTE_CARLO_RUNS
experiment.simulations[0].timesteps = TIMESTEPS
# Override default experiment System Parameters
experiment.simulations[0].model.params.update(parameter_overrides)
