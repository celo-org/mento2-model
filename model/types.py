"""
Various Python types used in the model
"""

# See https://docs.python.org/3/library/dataclasses.html
from enum import Enum
from typing import TypedDict

# Celo system types
Gas = int
Wei = int
Gwei = float
Gwei_per_Gas = float


# TODO: Do not rely on types Token_balance and TokenBalance, confusing
# TODO: Can we use positive-value-only datatypes for balances?
# TODO: Use decimal precision according to celo account balance precision
# Balance types
Token_balance = float
Usd_balance = float

# Price types
Usd_per_token = float
Token_per_token = float

# Simulation types
Run = int
Timestep = int

# Time-related types
Blocknumber = int
Day = int

# General types
Account_id = int


# Feature types
class Features(Enum):
    """Feature categories of Mento2"""

    BUY_AND_SELL_STABLES = 1
    """Mento1 like exchange that allows to buy (sell) stables into (out of) existence"""
    BORROW_AND_REPAY_STABLES = 2
    """IRPs that allow to borrow_and_repay (repay) stables into (out of) existence """
    SECURE_STABLES = 3
    """Stability providers"""


# TODO: Is there a better type for the below classes then TypedDicts?
class TokenBalance(TypedDict):
    """
    Class for an on-chain token balance
    """
    cusd: Token_balance
    celo: Token_balance


class Account(TokenBalance):
    """
    Class for an on-chain account
    """
    account_id: int
