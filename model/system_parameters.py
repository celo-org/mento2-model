"""
Definition of System Parameters, their types, and default values.

By using a dataclass to represent the System Parameters:
* We can use types for Python type hints
* Set default values
* Ensure that all System Parameters are initialized
"""

from dataclasses import dataclass
from datetime import datetime
from types import FunctionType
from typing import List
import experiments.simulation_configuration as simulation
from model.generators.markets import MarketPriceModel

from model.types import Blocknumber

from model.utils import default

# pylint: disable=too-many-instance-attributes


@dataclass
class Parameters:
    """System Parameters
    Each System Parameter is defined as:
    system parameter key: system parameter type = default system parameter value

    Because lists are mutable, we need to wrap each parameter list in the
     `default(...)` method.

    """

    # Time-related parameters
    # pylint: disable=invalid-name
    dt: List[Blocknumber] = default([simulation.BLOCKS_PER_TIMESTEP])
    """
    Simulation timescale / timestep unit of time, in blocks.

    Used to scale calculations that depend on the number of blocks that have passed.

    For example, for dt = 100, each timestep equals 100 blocks.

    """

    date_stability_providers: List[datetime] = default(
        [datetime.strptime("2022/10/01", "%Y/%m/%d")]
    )
    """
    Expected date for when stability providers can become active
    """

    date_irps: List[datetime] = default([datetime.strptime("2022/03/1", "%Y/%m/%d")])
    """
    Expected date for when IRPs can be used to mint stabletokens

    """

    # Mento1.0-related parameters
    cusd_demand: List[float] = default([10000000])
    reserve_fraction: List[float] = default([0.01])
    spread: List[float] = default([0.0025])
    max_sell_amount: List[float] = default([0.10])
    bucket_update_frequency_seconds: List[int] = default([5 * 60])

    # Market parameters for MarketPriceGenerator
    model: List[MarketPriceModel] = default([MarketPriceModel.GBM])
    covariance_market_price: List[float] = default([[[1, 0], [0, 1]]])
    drift_market_price: List[float] = default([[0, 0]])
    # data_file: List[str] = default(['mock_logreturns.csv'])
    custom_impact: List[FunctionType] = default(
        [lambda asset_1, asset_2: asset_1**2 / asset_2]
    )


# Initialize Parameters instance with default values
parameters = Parameters().__dict__
