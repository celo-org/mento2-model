"""
Various Python types used in the model
"""

# See https://docs.python.org/3/library/dataclasses.html
from typing import TypedDict

from enum import Enum

from model.generators.markets import MarketPriceGenerator

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

class AccountType(Enum):
    """
    different account holders
    """
    ARB_TRADER = "arb_trader"
    RANDOM_TRADER = "random_trader"
    CONTRACT = "contract"


# TODO: Is there a better type for the below classes then TypedDicts?
class AccountBalance(TypedDict):
    """
    Class for an on-chain token balance
    """

    cusd: float
    celo: float


class Account(AccountBalance):
    """
    Class for an on-chain account
    """
    # pylint: disable=too-few-public-methods
    account_id: int
    account_name: object


class MarketPrice(TypedDict):
    cusd_usd: float


# Todo Solve naming conflict


class MarketPriceG(TypedDict):
    cusd_usd: MarketPriceGenerator


class VirtualTanks(TypedDict):
    usd: float


class Actor(TypedDict):
    """
    Class for a single actor
    """

    actor_id: int
    account: Account


class OrderBook(TypedDict):
    ask_price: float
    bid_price: float
    last_price: float
    volume: float
