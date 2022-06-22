"""
Definition of System Parameters, their types, and default values.
By using a dataclass to represent the System Parameters:
* We can use types for Python type hints
* Set default values
* Ensure that all System Parameters are initialized
"""

from typing import List, Dict, TypedDict
from QuantLib import GeometricBrownianMotionProcess

from model.entities.balance import Balance
from model.types.base import (
    CryptoAsset,
    Currency,
    Fiat,
    ImpactDelayType,
    MarketPriceModel,
    MentoExchange,
    OracleType,
    Stable,
    TraderType,
)
from model.types.pair import Pair
from model.types.configs import (
    MarketPriceConfig,
    MentoExchangeConfig,
    OracleConfig,
    TraderConfig,
    ImpactDelayConfig
)
from model.utils.rng_provider import RNGProvider


class Parameters(TypedDict):
    """
    System Parameters as they are passed to a simulation run
    after the parameter sweep.
    Used as type annotation for functions that take params.
    """
    rng_seed: int
    rngp: RNGProvider
    mento_exchanges_config: Dict[Stable, MentoExchangeConfig]
    mento_exchanges_active: List[MentoExchange]
    market_price_model: MarketPriceModel
    market_price_processes: List[MarketPriceConfig]
    market_price_correlation_matrix: List[List[float]]
    average_daily_volume: Dict[Pair, float]
    impact_delay: ImpactDelayConfig
    impacted_assets: List[Pair]
    variance_market_price: Dict[Currency, Dict[Fiat, float]]
    traders: List[TraderConfig]
    reserve_inventory: Dict[Currency, float]
    reserve_target_weight: float
    oracles: List[OracleConfig]


class InitParameters(TypedDict):
    """System Parameters
    Each System Parameter is defined as:
    system parameter key: system parameter type = default system parameter value
    """
    rng_seed: List[int]
    mento_exchanges_config: List[Dict[Stable, MentoExchangeConfig]]
    mento_exchanges_active: List[List[MentoExchange]]
    market_price_model: List[MarketPriceModel]
    market_price_processes: List[List[MarketPriceConfig]]
    market_price_correlation_matrix: List[List[List[float]]]
    average_daily_volume: List[Dict[Pair, float]]
    impact_delay: List[ImpactDelayConfig]
    impacted_assets: List[List[Pair]]
    variance_market_price: List[Dict[Currency, Dict[Fiat, float]]]
    traders: List[List[TraderConfig]]
    reserve_inventory: List[Dict[Currency, float]]
    reserve_target_weight: List[float]
    oracle_pairs: List[List[Pair]]
    oracles: List[List[OracleConfig]]


parameters = InitParameters(
    rng_seed=[1000],
    # Configuration params for each stable's exchange
    mento_exchanges_config=[{
        MentoExchange.CUSD_CELO: MentoExchangeConfig(
            reserve_asset=CryptoAsset.CELO,
            stable=Stable.CUSD,
            reference_fiat=Fiat.USD,
            reserve_fraction=0.1,
            spread=0.0025,
            bucket_update_frequency_second=5*60,
            max_sell_fraction_of_float=0.0001
        ),
        MentoExchange.CEUR_CELO: MentoExchangeConfig(
            reserve_asset=CryptoAsset.CELO,
            stable=Stable.CEUR,
            reference_fiat=Fiat.EUR,
            reserve_fraction=0.1,
            spread=0.0025,
            bucket_update_frequency_second=5*60,
            max_sell_fraction_of_float=0.0001
        ),
        MentoExchange.CREAL_CELO: MentoExchangeConfig(
            reserve_asset=CryptoAsset.CELO,
            stable=Stable.CREAL,
            reference_fiat=Fiat.BRL,
            reserve_fraction=0.1,
            spread=0.0025,
            bucket_update_frequency_second=5*60,
            max_sell_fraction_of_float=0.0001
        ),
    }],
    mento_exchanges_active=[[
        MentoExchange.CUSD_CELO,
        MentoExchange.CEUR_CELO,
        MentoExchange.CREAL_CELO
    ]],

    # Market parameters for MarketPriceGenerator
    market_price_model=[MarketPriceModel.QUANTLIB],

    # check order of parameters for each model, e.g. for GBM param_1 is drift and
    # param_2 is volatility
    market_price_processes=[
        [
            MarketPriceConfig(
                pair=Pair(CryptoAsset.CELO, Fiat.USD),
                process=GeometricBrownianMotionProcess,
                param_1=0,
                param_2=1,
            ),
            MarketPriceConfig(
                pair=Pair(CryptoAsset.CELO, Fiat.EUR),
                process=GeometricBrownianMotionProcess,
                param_1=0,
                param_2=1,
            ),
            MarketPriceConfig(
                pair=Pair(CryptoAsset.CELO, Fiat.BRL),
                process=GeometricBrownianMotionProcess,
                param_1=0,
                param_2=1,
            ),
            MarketPriceConfig(
                pair=Pair(CryptoAsset.BTC, Fiat.USD),
                process=GeometricBrownianMotionProcess,
                param_1=0,
                param_2=0.1,
            ),
            MarketPriceConfig(
                pair=Pair(CryptoAsset.ETH, Fiat.USD),
                process=GeometricBrownianMotionProcess,
                param_1=0,
                param_2=0.2,
            ),
            MarketPriceConfig(
                pair=Pair(CryptoAsset.DAI, Fiat.USD),
                process=GeometricBrownianMotionProcess,
                param_1=0,
                param_2=0.001,
            ),
            MarketPriceConfig(
                pair=Pair(Stable.CUSD, Fiat.USD),
                process=GeometricBrownianMotionProcess,
                param_1=0,
                param_2=0.01,
            ),
            MarketPriceConfig(
                pair=Pair(Stable.CEUR, Fiat.EUR),
                process=GeometricBrownianMotionProcess,
                param_1=0,
                param_2=0.015,
            ),
            MarketPriceConfig(
                pair=Pair(Stable.CREAL, Fiat.BRL),
                process=GeometricBrownianMotionProcess,
                param_1=0,
                param_2=0.02,
            ),
        ]
    ],

    market_price_correlation_matrix=[
        [
            [1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 1],
        ]
    ],

    average_daily_volume=[{
        Pair(CryptoAsset.CELO, Fiat.USD): 1000000,
        Pair(CryptoAsset.CELO, Fiat.EUR): 1000000,
        Pair(CryptoAsset.CELO, Fiat.BRL): 1000000,
        Pair(Stable.CUSD, Fiat.USD): 1000000,
        Pair(Stable.CEUR, Fiat.EUR): 1000000,
        Pair(Stable.CREAL, Fiat.BRL): 1000000,
        Pair(CryptoAsset.BTC, Fiat.USD): 1000000,
        Pair(CryptoAsset.ETH, Fiat.USD): 1000000,
        Pair(CryptoAsset.DAI, Fiat.USD): 1000000,
    }],

    impact_delay=[
        ImpactDelayConfig(
            model=ImpactDelayType.NBLOCKS,
            param_1=10
        )
    ],
    impacted_assets=[[
        Pair(CryptoAsset.CELO, Fiat.USD),
        Pair(Stable.CUSD, Fiat.USD),
        Pair(Stable.CEUR, Fiat.EUR),
        Pair(Stable.CREAL, Fiat.BRL),
        Pair(CryptoAsset.BTC, Fiat.USD),
        Pair(CryptoAsset.ETH, Fiat.USD),
        Pair(CryptoAsset.DAI, Fiat.USD),
    ]],

    variance_market_price=[{
        Pair(CryptoAsset.CELO, Fiat.USD): 1,
        Pair(Stable.CUSD, Fiat.USD): 0.01,
        Pair(Stable.CEUR, Fiat.EUR): 0.01,
        Pair(Stable.CREAL, Fiat.BRL): 0.01,
        Pair(CryptoAsset.BTC, Fiat.USD): 0.1,
        Pair(CryptoAsset.ETH, Fiat.USD): 0.2,
        Pair(CryptoAsset.DAI, Fiat.USD): 0.001,
    }],

    traders=[
        [
            TraderConfig(
                trader_type=TraderType.ARBITRAGE_TRADER,
                count=1,
                balance=Balance({CryptoAsset.CELO: 500000, Stable.CUSD: 1000000}),
                exchange=MentoExchange.CUSD_CELO
            ),
            TraderConfig(
                trader_type=TraderType.ARBITRAGE_TRADER,
                count=2,
                balance=Balance({CryptoAsset.CELO: 500000, Stable.CEUR: 1000000}),
                exchange=MentoExchange.CEUR_CELO
            ),
        ]
    ],

    reserve_inventory=[{
        CryptoAsset.CELO: 10000000.0,
        CryptoAsset.BTC: 1000.0,
        CryptoAsset.ETH: 15000.0,
        CryptoAsset.DAI: 80000000.0,
    }],

    reserve_target_weight=[0.5
                           ],

    oracle_pairs=[[
        Pair(CryptoAsset.CELO, Fiat.USD),
        Pair(CryptoAsset.CELO, Fiat.EUR),
        Pair(CryptoAsset.CELO, Fiat.BRL),
    ]],
    oracles=[
        [
            OracleConfig(count=1,
                         type=OracleType.SINGLE_SOURCE,
                         aggregation=None,
                         delay=10,
                         price_threshold=0.02,
                         reporting_interval=6,
                         ),
        ]
    ]

)
