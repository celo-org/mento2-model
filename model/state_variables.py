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
    AccountBalance,
    TokenPerToken,
    TokenBalance,
    TokenPriceInUSD,
    TokenPriceInToken,
    Account,
    MarketPrice,
    VirtualTanks,
)

from data.historical_values import celo_price_mean, celo_supply_mean, cusd_supply_mean


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
    # celo_price: Usd_per_token = celo_price_mean
    # """The CELO spot price in USD"""
    # cusd_price: Usd_per_token = 1.0
    # """The CELO spot price"""
    mento_rate: TokenPerToken = celo_price_mean
    """The Mento CELO/cUSD rate """

    # Reserve state variable
    reserve_account: Account = default(
        {"account_id": 0, "celo": 120000000.0, "cusd": 0.0}
    )

    # Mento state variables
    mento_buckets: TokenBalance = default({"celo": 0.0, "cusd": 0.0})

    # Mento state variables
    floating_supply: TokenBalance = default(
        {"celo": celo_supply_mean, "cusd": cusd_supply_mean}
    )

    # Virtual Fiat Market Tank
    virtual_tanks: VirtualTanks = default({"usd": cusd_supply_mean})

    market_price: MarketPrice = default({"cusd_usd": 1, "celo_usd": 3})

    number_of_accounts: int = default(1)

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
    # Celo state variables
    celo_usd_price: TokenPriceInUSD = celo_price_mean
    """The CELO spot price in USD"""
    cusd_usd_price: TokenPriceInUSD = 1.0
    """The CELO spot price"""

    # Reserve balance
    reserve_balance: TokenBalance = default({"celo": 120000000.0, "cusd": 0.0})

    # Mento state variables
    mento_buckets: AccountBalance = default({"celo": 0.0, "cusd": 0.0})

    mento_rate: TokenPriceInToken = celo_price_mean
    """The Mento CELO/cUSD rate """


# Initialize State Variables instance with default values
initial_state = StateVariables().__dict__
