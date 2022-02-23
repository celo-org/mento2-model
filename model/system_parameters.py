"""
Definition of System Parameters, their types, and default values.
By using a dataclass to represent the System Parameters:
* We can use types for Python type hints
* Set default values
* Ensure that all System Parameters are initialized
"""

from dataclasses import dataclass
from typing import List
import experiments.simulation_configuration as simulation
from model.types import Blocknumber
from model.utils import default


@dataclass
class Parameters:
    """System Parameters
    Each System Parameter is defined as:
    system parameter key: system parameter type = default system parameter value
    Because lists are mutable, we need to wrap each parameter list in the `default(...)` method.
    """

    # Time-related parameters
    dt: List[Blocknumber] = default([simulation.BLOCKS_PER_TIMESTEP])
    """
    Simulation timescale / timestep unit of time, in blocks.
    Used to scale calculations that depend on the number of blocks that have passed.
    For example, for dt = 100, each timestep equals 100 blocks.
    """

    # Buy_and_sell-related parameters
    cusd_demand: List[float] = default([10000000])
    reserve_fraction: List[float] = default([0.01])
    spread: List[float] = default([0.0025])
    max_sell_fraction_of_float: List[float] = default(
        [0.0001])  # Max 0.01% of CELO or cUSD float sold in every block
    bucket_update_frequency_seconds: List[int] = default([5 * 60])


# Initialize Parameters instance with default values
parameters = Parameters().__dict__
