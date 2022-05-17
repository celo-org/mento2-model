"""
Various Python types used in the model
"""

# See https://docs.python.org/3/library/dataclasses.html
from typing import TypedDict

from enum import Enum

from model.generators.markets import MarketPriceGenerator
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

class MarketPrice(TypedDict):
    cusd_usd: float


# Todo Solve naming conflict
class MarketPriceG(TypedDict):
    cusd_usd: MarketPriceGenerator


class MarketBuckets(TypedDict):
    usd: float
