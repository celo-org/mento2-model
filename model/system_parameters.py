"""
Definition of System Parameters, their types, and default values.
By using a dataclass to represent the System Parameters:
* We can use types for Python type hints
* Set default values
* Ensure that all System Parameters are initialized
"""

from dataclasses import dataclass
from typing import List, Dict

import experiments.simulation_configuration as simulation

from model.entities.balance import Balance
from model.generators.markets import MarketPriceModel
from model.types import (
    Blocknumber,
    Crypto,
    Currency,
    Fiat,
    MentoExchange,
    MentoExchangeConfig,
    Stable,
    TraderConfig,
    TraderType,
)
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
    ceur_demand: List[float] = default([100000])
    creal_demand: List[float] = default([1000])

    """
    Configuration params for each stable's exchange
    """
    mento_exchanges_config: List[Dict[Stable, MentoExchangeConfig]] = default([{
        MentoExchange.CUSD_CELO: MentoExchangeConfig(
            stable=Stable.CUSD,
            stable_fiat=Fiat.USD,
            base=Crypto.CELO,
            reserve_fraction=0.1,
            spread=0.0025,
            bucket_update_frequency_second=5*60,
            max_sell_fraction_of_float=0.0001
        ),
        MentoExchange.CEUR_CELO: MentoExchangeConfig(
            stable=Stable.CEUR,
            stable_fiat=Fiat.EUR,
            base=Crypto.CELO,
            reserve_fraction=0.1,
            spread=0.0025,
            bucket_update_frequency_second=5*60,
            max_sell_fraction_of_float=0.0001
        ),
        MentoExchange.CREAL_CELO: MentoExchangeConfig(
            stable=Stable.CREAL,
            stable_fiat=Fiat.BRL,
            base=Crypto.CELO,
            reserve_fraction=0.1,
            spread=0.0025,
            bucket_update_frequency_second=5*60,
            max_sell_fraction_of_float=0.0001
        ),
    }])

    """
    List of active mento exchanges
    """
    mento_exchanges_active: List[List[MentoExchange]] = default([[
        MentoExchange.CUSD_CELO,
        MentoExchange.CEUR_CELO,
        MentoExchange.CREAL_CELO
    ]])


    # Market parameters for MarketPriceGenerator
    model: List[MarketPriceModel] = default([MarketPriceModel.GBM])
    covariance_market_price: List[float] = default([[[0.01, 0], [0, 1]]])
    drift_market_price: List[float] = default([[-5*5, 0]])
    # data_file: List[str] = default(['mock_logreturns.csv'])
    # custom_impact: List[FunctionType] = default(
    #    [lambda asset_1, asset_2: asset_1**2 / asset_2]
    # )

    average_daily_volume: List[Dict[Currency, Dict[Fiat, float]]] = default([
        {
            Crypto.CELO: {
                Fiat.USD: 1000000,
                Fiat.EUR: 1000000,
                Fiat.BRL: 1000000
            },
            Stable.CUSD: {
                Fiat.USD: 1000000,
            },
            Stable.CEUR: {
                Fiat.EUR: 1000000,
            },
            Stable.CREAL: {
                Fiat.BRL: 1000000,
            },
        }
    ])

    traders: List[List[TraderConfig]] = default(
        [
            TraderConfig(
                trader_type=TraderType.ARBITRAGE_TRADER,
                count=1,
                balance=Balance(celo=500000, cusd=1000000),
                exchange=MentoExchange.CUSD_CELO
            ),
            TraderConfig(
                trader_type=TraderType.ARBITRAGE_TRADER,
                count=2,
                balance=Balance(celo=500000, ceur=1000000),
                exchange=MentoExchange.CEUR_CELO
            ),
        ]
    )

    reserve_inventory: List[Dict[Currency, float]] = default([{
        Crypto.CELO: 12000000,
    }])


# Initialize Parameters instance with default values
parameters = Parameters().__dict__
