"""
Helper functions to generate stochastic environmental processes
"""

import numpy as np
import experiments.simulation_configuration as simulation_configuration
from stochastic import processes
from data import historical_values
from experiments.utils import rng_generator


def create_cusd_demand_process(
    timesteps=simulation_configuration.TIMESTEPS,
    timesteps_per_year=simulation_configuration.TIMESTEPS_PER_YEAR,
    dt=simulation_configuration.DELTA_TIME,
    initial_cusd_demand=historical_values.cusd_supply_mean,
    cusd_demand_returns_vola_annually=historical_values.cusd_supply_returns_vola_annually,
    rng=np.random.default_rng(1)
):
    """Configure environmental cUSD demand process

    > A GBM with starting value of initial_cusd_demand
    See https://stochastic.readthedocs.io/en/latest/continuous.html
    """
    per_timestep_volatility = cusd_demand_returns_vola_annually / timesteps_per_year
    process = processes.continuous.GeometricBrownianMotion(drift=0.0, volatility=1.0, t=(timesteps * dt), rng=rng)
    samples = process.sample(timesteps * dt + 1)
    samples = np.multiply(initial_cusd_demand, samples)

    return samples


def create_stochastic_process_realizations(
    process,
    timesteps=simulation_configuration.TIMESTEPS,
    dt=simulation_configuration.DELTA_TIME,
    runs=5,
):
    """Create stochastic process realizations

    Using the stochastic processes defined in `processes` module, create random number generator (RNG) seeds,
    and use RNG to pre-generate samples for number of simulation_configuration timesteps.
    """

    switcher = {
        "cusd_demand_process": [
            create_cusd_demand_process(timesteps=timesteps, dt=dt, rng=rng_generator())
            for _ in range(runs)
        ]
    }

    return switcher.get(process, "Invalid Process")
