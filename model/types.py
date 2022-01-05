"""
Various Python types used in the model
"""

# See https://docs.python.org/3/library/dataclasses.html
from dataclasses import dataclass, field
from enum import Enum
from typing import TypedDict, List, Callable, NamedTuple

# Ethereum system types
Gas = int
Wei = int
Gwei = float
Gwei_per_Gas = float
CELO = float  # Should we use decimals package for these types?


class Stage(Enum):
    """Stages of the Mento1.0 -> Mento2.0 upgrade process network upgrade process"""

    Mento1 = 1
    Mento1_plus_stability_providers = 2


# Balance types
CELO = float
CUSD = float
USD = float

# Simulation types
Run = int
Timestep = int

# Time-related types
Block = int
Day = int


@dataclass
class Account(TypedDict):
    """
    Class for an on-chain account
    """
    account_id: int
    cusd: CUSD
    celo: CELO


@dataclass
class Actor:
    """
    Class for a single actor
    """
    actor_id: int
    account: Account
