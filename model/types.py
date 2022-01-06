"""
Various Python types used in the model
"""

# See https://docs.python.org/3/library/dataclasses.html
from dataclasses import dataclass, field
from enum import Enum

# Celo system types
Gas = int
Wei = int
Gwei = float
Gwei_per_Gas = float


class Stage(Enum):
    """Stages of the Mento1.0 -> Mento2.0 upgrade process network upgrade process"""

    Mento1 = 1
    Mento1_plus_stability_providers = 2


# Balance types
Tokens = float
Usd = float

# Price types
Usd_per_token = float
Token_per_token = float

# Simulation types
Run = int
Timestep = int

# Time-related types
Blocknumber = int
Day = int


@dataclass
class Account:
    """
    Class for an on-chain account
    """
    account_id: int
    cusd: CUSD
    celo: CELO

@dataclass
class MentoBuckets:
    """
    Class for mento buckets
    """
    cusd: CUSD
    celo: CELO


@dataclass
class Actor:
    """
    Class for a single actor
    """
    actor_id: int
    account: Account
