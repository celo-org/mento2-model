"""
Definition of State Variables, their types, and default values.
By using a dataclass to represent the State Variables:
* We can use types for Python type hints
* Set default values
* Ensure that all State Variables are initialized
"""

from dataclasses import dataclass
from model.utils import default

from model.types import (
    TokenPriceInUSD,
    TokenPriceInToken,
    AccountBalance,
    TokenBalance
)
from data.historical_values import (
    celo_price_mean,
    celo_supply_mean,
    cusd_supply_mean
)


@dataclass
class StateVariables:
    """State Variables
    Each State Variable is defined as:
    state variable key: state variable type = default state variable value
    """

    # Floating supply state variables
    floating_supply: TokenBalance = default(
        {
            'celo': celo_supply_mean,
            'cusd': cusd_supply_mean
        }
    )

    # Celo state variables
    celo_usd_price: TokenPriceInUSD = celo_price_mean
    """The CELO spot price in USD"""
    cusd_usd_price: TokenPriceInUSD = 1.0
    """The CELO spot price"""

    # Reserve balance
    reserve_balance: TokenBalance = default(
        {
            'celo': 120000000.0,
            'cusd': 0.0
        }
    )

    # Mento state variables
    mento_buckets: AccountBalance = default(
        {
            'celo': 0.0,
            'cusd': 0.0
        }
    )

    mento_rate: TokenPriceInToken = celo_price_mean
    """The Mento CELO/cUSD rate """



# Initialize State Variables instance with default values
initial_state = StateVariables().__dict__
