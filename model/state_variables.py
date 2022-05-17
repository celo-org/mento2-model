"""
Definition of State Variables, their types, and default values.
By using a dataclass to represent the State Variables:
* We can use types for Python type hints
* Set default values
* Ensure that all State Variables are initialized
"""


from dataclasses import dataclass
from datetime import datetime
from typing import Dict
from model.utils import default

from model.types import (
    TokenPerToken,
    TokenBalance,
    MarketPrice,
    MarketBuckets,
)

from data.historical_values import  celo_supply_mean, cusd_supply_mean


@dataclass
class StateVariables:
    """State Variables
    Each State Variable is defined as:
    state variable key: state variable type = default state variable value
    """

    # pylint: disable=too-many-instance-attributes
    # Time state variables
    timestamp: datetime = None
    """
    The timestamp for each timestep as a Python `datetime` object, starting
    from `date_start` Parameter.
    """

    # Celo state variables
    oracle_rate: TokenPerToken = 3
    """The Mento CELO/cUSD rate """

    # Reserve state variable
    reserve_balance: Dict[str, TokenBalance] = default(
        {"celo": 120000000.0, "cusd": 0.0}
    )

    # Mento state variables
    # TODO initial calibration of buckets
    mento_buckets: Dict[str, TokenBalance] = default(
        {
            "celo": 0.025 * 1200000000,
            "cusd": 0.025 * 1200000000 * oracle_rate,
        }
    )

    # Mento state variables
    floating_supply: TokenBalance = default(
        {"celo": celo_supply_mean, "cusd": cusd_supply_mean}
    )

    # Virtual Market Fiat Bucket
    market_buckets: MarketBuckets = default({"usd": cusd_supply_mean})

    market_price: MarketPrice = default({"cusd_usd": 1, "celo_usd": 3})

    number_of_accounts: int = default(1)


# Initialize State Variables instance with default values
initial_state = StateVariables().__dict__
