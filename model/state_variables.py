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
    AccountBalance
)
from data.historical_values import (
    celo_price_mean,
)


@dataclass
class StateVariables:
    """State Variables
    Each State Variable is defined as:
    state variable key: state variable type = default state variable value
    """

    # Celo state variables
    celo_usd_price: TokenPriceInUSD = celo_price_mean
    """The CELO spot price in USD"""
    cusd_usd_price: TokenPriceInUSD = 1.0
    """The CELO spot price"""

    # TODO: variable to track reserve balance from accounts

    # Mento state variables
    mento_buckets: AccountBalance = default(
        {
            'celo': 0.0,
            'cusd': 0.0
        }
    )

    mento_rate: TokenPriceInToken = celo_price_mean
    """The Mento CELO/cUSD rate """

    # Floating supply state variables
    # TODO: Floating supply variables to track floating supply as calulated by accounts Generator
    # floating_supply_celo


# Initialize State Variables instance with default values
initial_state = StateVariables().__dict__
