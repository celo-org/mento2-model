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
    Usd_per_token,
    Token_per_token,
    Token_balance,
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

    # Celo state variables
    celo_usd_price: Usd_per_token = celo_price_mean
    """The CELO spot price in USD"""
    cusd_usd_price: Usd_per_token = 1.0
    """The CELO spot price"""
    num_accounts: int = 0

    # Reserve state variable
    reserve_balance: TokenBalance = default(
        {
            'celo': 120000000.0,
            'cusd': 0.0
        }
    )

    # Mento state variables
    mento_buckets: TokenBalance = default(
        {
            'celo': 0.0,
            'cusd': 0.0
        }
    )

    mento_rate: Token_per_token = celo_price_mean
    """The Mento CELO/cUSD rate """

    # Floating supply state variables
    # TODO: Bring this in line with the account manager tracking total supplies
    floating_supply: TokenBalance = default(
        {
            'celo': celo_supply_mean,
            'cusd': cusd_supply_mean
        }
    )

    # IRP related state variables
    total_celo_lend: Token_balance = default(0)
    total_cusd_borrowed: Token_balance = default(0)


# Initialize State Variables instance with default values
initial_state = StateVariables().__dict__
