"""
Definition of State Variables, their types, and default values.

By using a dataclass to represent the State Variables:
* We can use types for Python type hints
* Set default values
* Ensure that all State Variables are initialized
"""


from dataclasses import dataclass
from datetime import datetime
from model.utils import default

from model.types import (
    Usd_per_token,
    Token_per_token,
    TokenBalance,
    Account,
    MarketPrice,
    VirtualTanks
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

    # Time state variables
    timestamp: datetime = None
    """
    The timestamp for each timestep as a Python `datetime` object, starting from `date_start` Parameter.
    """

    # Celo state variables
    #celo_price: Usd_per_token = celo_price_mean
    #"""The CELO spot price in USD"""
    #cusd_price: Usd_per_token = 1.0
    #"""The CELO spot price"""
    mento_rate: Token_per_token = celo_price_mean
    """The Mento CELO/cUSD rate """

    # Reserve state variable
    reserve_account: Account = default(
        {
            'account_id': 0,
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

    # Mento state variables
    floating_supply: TokenBalance = default(
        {
            'celo': celo_supply_mean,
            'cusd': cusd_supply_mean
        }
    )

    # Virtual Fiat Market Tank
    virtual_tanks: VirtualTanks = default(
        {
            'usd': cusd_supply_mean
        }
    )

    market_price: MarketPrice = default(
        {
            'cusd_usd': 1,
            'celo_usd': 3
        }
    )

    # _demand_generator: Demand = default(
    #     {
    #          DemandGenerator().parse_from_parameters(parameters)
    #     }
    # )

    # # CEX state variables
    # order_book: OrderBook  = default(
    #     {
    #         'bid_price': bid_price,
    #         'ask_price': ask_price,
    #         'mid_price': mid_price',
    #         'last_price': last_price,
    #         'volume': volume
    #     }
    #
    # )


# Initialize State Variables instance with default values
initial_state = StateVariables().__dict__
