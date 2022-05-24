"""
Various Python types used in the model
"""

# See https://docs.python.org/3/library/dataclasses.html
from dataclasses import dataclass
from typing import Dict, TypedDict

from enum import Enum
from model.entities.balance import Balance

from model.entities.strategies import RandomTrading, SellMax, ArbitrageTrading

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

    ARBITRAGE_TRADER = ArbitrageTrading
    RANDOM_TRADER = RandomTrading
    MAX_TRADER = SellMax


@dataclass
class TraderConfig:
    count: int
    balance: Balance


Traders = Dict[TraderType, TraderConfig]


class MarketPrice(TypedDict):
    cusd_usd: float


class MarketBuckets(TypedDict):
    usd: float


class MarketPriceModel(Enum):
    QUANTLIB = "quantlib"
    PRICE_IMPACT = "price_impact"
    HIST_SIM = "hist_sim"
    SCENARIO = "scenario"


class PriceImpact(Enum):
    ROOT_QUANTITY = "root_quantity"
    CUSTOM = "custom"


class ImpactDelay(Enum):
    INSTANT = "instant"
    NBLOCKS = "nblocks"
