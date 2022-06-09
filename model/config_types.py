"""
Typing for Configs
"""

from typing import Any, NamedTuple, Set
from model.entities.balance import Balance

from model.types import (AggregationMethod,
                         CryptoAsset,
                         Fiat,
                         ImpactDelayType,
                         MentoExchange,
                         OracleType,
                         Pair, Stable,
                         TraderType)


class TraderConfig(NamedTuple):
    trader_type: TraderType
    count: int
    balance: Balance
    exchange: MentoExchange


class MentoExchangeConfig(NamedTuple):
    reserve_asset: CryptoAsset
    stable: Stable
    reference_fiat: Fiat
    reserve_fraction: float
    spread: float
    bucket_update_frequency_second: int
    max_sell_fraction_of_float: float


class MarketPriceConfig(NamedTuple):
    pair: Pair
    process: Any
    param_1: float
    param_2: float


class OracleConfig(NamedTuple):
    type: OracleType
    count: int
    aggregation: AggregationMethod
    delay: int
    reporting_interval: int
    price_threshold: int
    pairs: Set[Pair]


class ImpactDelayConfig(NamedTuple):
    model: ImpactDelayType
    param_1: float
