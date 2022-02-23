"""
Various Python types used in the model
"""

# See https://docs.python.org/3/library/dataclasses.html
from typing import TypedDict

# Celo system types
Gas = int
Wei = int
Gwei = float
GweiPerGas = float

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


# TODO: Is there a better type for the below classes then TypedDicts?
class AccountBalance(TypedDict):
    """
    Class for an on-chain token balance
    """
    cusd: TokenBalance
    celo: TokenBalance


class Account(AccountBalance):
    """
    Class for an on-chain account
    """
    account_id: int
    account_name: object
