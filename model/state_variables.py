"""
Definition of State Variables, their types, and default values.

By using a dataclass to represent the State Variables:
* We can use types for Python type hints
* Set default values
* Ensure that all State Variables are initialized
"""


from dataclasses import dataclass, fields
from datetime import datetime

from model.types import (
    CELO,
    CUSD,
    USD_per_CELO,
    Account,
    MentoBuckets
)
from data.historical_values import (
    celo_price_mean,
    celo_supply_mean,
    cusd_price_mean,
    cusd_supply_mean
)


@dataclass
class StateVariables:
    """State Variables
    Each State Variable is defined as:
    state variable key: state variable type = default state variable value
    """

    # Time state variables
    timestamp: datetime = None
    """
    The timestamp for each timestep as a Python `datetime` object, starting from `date_start` Parameter.
    """

    # Celo state variables
    celo_price: USD_per_CELO = celo_price_mean
    """The CELO spot price"""
    celo_supply: CELO = celo_supply_mean
    """The total CELO supply"""
    cusd_price: USD_per_CUSD= cusd_price_mean
    """The CELO spot price"""
    cusd_supply: CUSD = cusd_supply_mean
    """The total CELO supply"""

    # Reserve state variable
    reserve_account: Account = fields(
        Account(
            account_id=0,
            celo=120000000,
            cusd=0
        )
    )

    # Mento state variables
    mento_buckets: MentoBuckets = fields(
        MentoBuckets(
            celo=0,
            cusd=0
        )
    )


# Initialize State Variables instance with default values
initial_state = StateVariables().__dict__
