"""
Definition of System Parameters, their types, and default values.
By using a dataclass to represent the System Parameters:
* We can use types for Python type hints
* Set default values
* Ensure that all System Parameters are initialized
"""

from dataclasses import dataclass
from typing import List, Dict
from QuantLib import GeometricBrownianMotionProcess
import experiments.simulation_configuration as simulation

from model.entities.balance import Balance
from model.generators.markets import MarketPriceModel
from model.types import (
    Blocknumber,
    Crypto,
    Currency,
    Fiat,
    MarketPriceConfig,
    MentoExchange,
    MentoExchangeConfig,
    Pair,
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

    # Configuration params for each stable's exchange
    mento_exchanges_config: List[Dict[Stable, MentoExchangeConfig]] = default([{
        MentoExchange.CUSD_CELO: MentoExchangeConfig(
            reserve_asset=Crypto.CELO,
            stable=Stable.CUSD,
            peg=Fiat.USD,
            reserve_fraction=0.1,
            spread=0.0025,
            bucket_update_frequency_second=5*60,
            max_sell_fraction_of_float=0.0001
        ),
        MentoExchange.CEUR_CELO: MentoExchangeConfig(
            reserve_asset=Crypto.CELO,
            stable=Stable.CEUR,
            peg=Fiat.EUR,
            reserve_fraction=0.1,
            spread=0.0025,
            bucket_update_frequency_second=5*60,
            max_sell_fraction_of_float=0.0001
        ),
        MentoExchange.CREAL_CELO: MentoExchangeConfig(
            reserve_asset=Crypto.CELO,
            stable=Stable.CREAL,
            peg=Fiat.BRL,
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
    model: List[MarketPriceModel] = default([MarketPriceModel.QUANTLIB])

    # check order of parameters for each model, e.g. for GBM param_1 is drift and
    # param_2 is volatility
    market_price_processes: List[List[MarketPriceConfig]] = default([
        [
            MarketPriceConfig(
                pair=Pair(Crypto.CELO, Fiat.USD),
                process=GeometricBrownianMotionProcess,
                param_1=0,
                param_2=1,
            ),
            MarketPriceConfig(
                pair=Pair(Stable.CUSD, Fiat.USD),
                process=GeometricBrownianMotionProcess,
                param_1=0,
                param_2=0.01,
            ),
            MarketPriceConfig(
                pair=Pair(Crypto.BTC, Fiat.USD),
                process=GeometricBrownianMotionProcess,
                param_1=0,
                param_2=0.01,
            ),
        ]
    ])

    market_price_correlation_matrix: List[List[List[float]]] = default([
        [ [1, 0, 0],
          [0, 1, 0],
          [0, 0, 1] ]
    ])
    # TODO: is this used?
    # drift_market_price: List[float] = default([[-5*5, 0]])

    average_daily_volume: List[Dict[Pair, float]] = default([{
        Pair(Crypto.CELO, Fiat.USD): 1000000,
        Pair(Crypto.CELO, Fiat.EUR): 1000000,
        Pair(Crypto.CELO, Fiat.BRL): 1000000,
        Pair(Stable.CUSD, Fiat.USD): 1000000,
        Pair(Stable.CEUR, Fiat.EUR): 1000000,
        Pair(Stable.CREAL, Fiat.BRL): 1000000,
    }])

    # Impact Parameters
    impacted_assets: List[List[Pair]] = default([[
        Pair(Crypto.CELO, Fiat.USD),
        Pair(Stable.CUSD, Fiat.USD),
        Pair(Stable.CEUR, Fiat.EUR),
        Pair(Stable.CREAL, Fiat.BRL),
    ]])

    variance_market_price: List[Dict[Currency, Dict[Fiat, float]]] = default([{
        Pair(Crypto.CELO, Fiat.USD): 1,
        Pair(Stable.CUSD, Fiat.USD): 1,
        Pair(Stable.CEUR, Fiat.EUR): 1,
        Pair(Stable.CREAL, Fiat.BRL): 1
    }])

    # Trader Balances
    traders: List[List[TraderConfig]] = default([
        [
            TraderConfig(
                trader_type=TraderType.ARBITRAGE_TRADER,
                count=1,
                balance=Balance({ Crypto.CELO: 500000, Stable.CUSD: 1000000 }),
                exchange=MentoExchange.CUSD_CELO
            ),
            TraderConfig(
                trader_type=TraderType.ARBITRAGE_TRADER,
                count=2,
                balance=Balance({ Crypto.CELO: 500000, Stable.CEUR: 1000000 }),
                exchange=MentoExchange.CEUR_CELO
            ),
        ]
    ])

    reserve_inventory: List[Dict[Currency, float]] = default([{
        Crypto.CELO: 12000000,
    }])


# Initialize Parameters instance with default values
parameters = Parameters().__dict__
