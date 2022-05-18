"""
Definition of System Parameters, their types, and default values.
By using a dataclass to represent the System Parameters:
* We can use types for Python type hints
* Set default values
* Ensure that all System Parameters are initialized
"""

from dataclasses import dataclass
from typing import Any, List, Dict
from QuantLib import GeometricBrownianMotionProcess
import experiments.simulation_configuration as simulation
from model.entities.balance import Balance
from model.types import TraderType
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
    dt: List[Blocknumber] = default([simulation.BLOCKS_PER_TIMESTEP])
    """
    Simulation timescale / timestep unit of time, in blocks.
    Used to scale calculations that depend on the number of blocks that have passed.
    For example, for dt = 100, each timestep equals 100 blocks.
    """

    # Buy_and_sell-related parameters
    cusd_demand: List[float] = default([10000000])
    reserve_fraction: List[float] = default([0.1])
    spread: List[float] = default([0.0025])
    max_sell_fraction_of_float: List[float] = default(
        [0.0001]
    )  # Max 0.01% of CELO or cUSD float sold in every block
    bucket_update_frequency_seconds: List[int] = default([5 * 60])

    # Market parameters for MarketPriceGenerator
    model: List[MarketPriceModel] = default([MarketPriceModel.GBM])

    # check order of parameters for each model, e.g. for GBM param_1 is drift and
    # param_2 is volatility
    processes: List[Dict] = default(
        [
            {
                'celo_usd': {'process': GeometricBrownianMotionProcess,
                             'param_1': 0,
                             'param_2': 1},
                'cusd_usd': {'process': GeometricBrownianMotionProcess,
                             'param_1': 0,
                             'param_2': 0.01}
            }
        ]
    )
    correlation: List[float] = default([[[1, 0], [0, 1]]])
    drift_market_price: List[float] = default([[-5*5, 0]])
    # data_file: List[str] = default(['mock_logreturns.csv'])
    # custom_impact: List[FunctionType] = default(
    #    [lambda asset_1, asset_2: asset_1**2 / asset_2]
    # )
    average_daily_volume: List[Dict] = default(
        [{"celo_usd": 1000000, "cusd_usd": 1000000}]
    )
    variance_market_price: List[Dict] = default([{"celo_usd": 1, "cusd_usd": 0.01}])

    traders: List[Dict[TraderType, Dict[str, Any]]] = default(
        [
            {
                TraderType.ARBITRAGE_TRADER: dict(
                    count=1,
                    balance=Balance(celo=500000, cusd=1000000)
                )
            }
        ]
    )
    reserve_inventory: List[Dict] = default([{"celo": 120000000, "cusd": 0}])


# Initialize Parameters instance with default values
parameters = Parameters().__dict__
