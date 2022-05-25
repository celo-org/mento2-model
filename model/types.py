"""
Various Python types used in the model
"""

from typing import Any, Dict, NamedTuple, Union
from enum import Enum

from model.entities.balance import Balance

# Celo system types
Gas = int
Wei = int
Gwei = float
GweiPerGas = float

# Price types
UsdPerToken = float
TokenPerToken = float

# TODO: Use decimal precision according to celo account balance precision
# Balance types
TokenBalance = float

# Price types
TokenPriceInUSD = float
TokenPriceInToken = float

# Simulation types
Run = int
Timestep = int

# Time-related types
Blocknumber = int
Day = int

class TraderType(Enum):
    """
    different account holders
    """
    ARBITRAGE_TRADER = "ArbitrageTrading"
    RANDOM_TRADER = "RandomTrading"
    MAX_TRADER = "SellMax"

class Stable(Enum):
    """
    Celo Stable assets
    """
    CUSD = "cusd"
    CREAL = "creal"
    CEUR = "ceur"

class Crypto(Enum):
    CELO = "celo"
    ETH = "eth"
    BTC = "btc"
    DAI = "dai"

class Fiat(Enum):
    USD = "usd"
    EUR = "eur"
    BRL = "brl"

Currency = Union[Stable, Fiat, Crypto]
CurrencyRate = Dict[Currency, Dict[Currency, float]]
MarketBuckets = Dict[Currency, float]

class MentoExchange(Enum):
    CUSD_CELO = "cusd_celo"
    CREAL_CELO = "creal_celo"
    CEUR_CELO = "ceuro_celo"

class ReserveBalance(NamedTuple):
    celo: float
    btc: float
    dai: float
    eth: float

class MentoBuckets(NamedTuple):
    stable: float
    reserve_asset: float

class TraderConfig(NamedTuple):
    trader_type: TraderType
    count: int
    balance: Balance
    exchange: MentoExchange

class MentoExchangeConfig(NamedTuple):
    reserve_asset: Crypto
    stable: Stable
    peg: Fiat
    reserve_fraction: float
    spread: float
    bucket_update_frequency_second: int
    max_sell_fraction_of_float: float

class MarketPriceConfig(NamedTuple):
    base: Currency
    quote: Fiat
    process: Any
    param_1: float
    param_2: float
