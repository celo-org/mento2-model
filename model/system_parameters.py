"""
Definition of System Parameters, their types, and default values.

By using a dataclass to represent the System Parameters:
* We can use types for Python type hints
* Set default values
* Ensure that all System Parameters are initialized
"""

from dataclasses import dataclass
from datetime import datetime
import experiments.simulation_configuration as simulation
from model.types import (
    List,
    Block,
    Stage,
)

from model.utils import default


@dataclass
class Parameters:
    """System Parameters
    Each System Parameter is defined as:
    system parameter key: system parameter type = default system parameter value

    Because lists are mutable, we need to wrap each parameter list in the `default(...)` method.

    For default value assumptions, see the ASSUMPTIONS.md document.
    """

    # Time parameters
    dt: List[Block] = default([simulation.DELTA_TIME])
    """
    Simulation timescale / timestep unit of time, in blocks.

    Used to scale calculations that depend on the number of blocks that have passed.

    For example, for dt = 100, each timestep equals 100 blocks.

    """

    stage: List[Stage] = default([Stage.ALL])
    """
    Which stage or stages of the Mento1.0 -> Mento2.0 upgrade process to simulate.

    See model.types.Stage Enum for further documentation.
    """

    date_start: List[datetime] = default([datetime.now()])
    """Start date for simulation as Python datetime"""

    date_stability_providers: List[datetime] = default(
        [datetime.strptime("2022/10/01", "%Y/%m/%d")]
    )
    """
    Expected date for when stability providers can become active
    """

    date_irps: List[datetime] = default([datetime.strptime("2022/03/1", "%Y/%m/%d")])
    """
    Expected date for when IRPs can be used to mint stabletokens
    
    See ASSUMPTIONS.md doc for further details about default value assumption.
    """


# Initialize Parameters instance with default values
parameters = Parameters().__dict__
