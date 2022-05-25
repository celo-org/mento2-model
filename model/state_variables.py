"""
Definition of State Variables, their types, and default values.
By using a dataclass to represent the State Variables:
* We can use types for Python type hints
* Set default values
* Ensure that all State Variables are initialized
"""
# pylint: disable=too-many-instance-attributes

from dataclasses import dataclass
from typing import Dict, Union
from model.utils import default

from model.types import (
    Crypto,
    Fiat,
    MentoBuckets,
    MentoExchange,
    Pair,
    Stable,
    MarketBuckets,
)

from data.historical_values import (
    CELO_SUPPLY_MEAN,
    CUSD_SUPPLY_MEAN,
    CEUR_SUPPLY_MEAN,
    CREAL_SUPPLY_MEAN,
)


@dataclass
class StateVariables:
    """State Variables
    Each State Variable is defined as:
    state variable key: state variable type = default state variable value
    """

    # The initial floating supply of the simulation
    floating_supply: Dict[Union[Crypto, Stable], float] = default({
        Crypto.CELO: CELO_SUPPLY_MEAN,
        Stable.CUSD: CUSD_SUPPLY_MEAN,
        Stable.CEUR: CEUR_SUPPLY_MEAN,
        Stable.CREAL: CREAL_SUPPLY_MEAN,
    })

    oracle_rate: Dict[Pair, float] = default({
        Pair(Crypto.CELO, Fiat.USD): 3,
        Pair(Crypto.CELO, Fiat.EUR): 2.5,
        Pair(Crypto.CELO, Fiat.BRL): 15,
    })

    # Reserve state variable
    reserve_balance: Dict[Crypto, float] = default({
        Crypto.CELO: 120000000.0
    })
    # Mento state variables
    # TODO initial calibration of buckets
    mento_buckets: Dict[MentoExchange, MentoBuckets] = default({
        MentoExchange.CUSD_CELO: MentoBuckets(stable=0, reserve_asset=0),
        MentoExchange.CEUR_CELO: MentoBuckets(stable=0, reserve_asset=0),
        MentoExchange.CREAL_CELO: MentoBuckets(stable=0, reserve_asset=0),
    })


    # Virtual Market Fiat Bucket
    market_buckets: MarketBuckets = default({
        Fiat.USD: CUSD_SUPPLY_MEAN,
        Fiat.EUR: CEUR_SUPPLY_MEAN,
        Fiat.BRL: CREAL_SUPPLY_MEAN,
    })

    market_price: Dict[Pair, float] = default({
        Pair(Crypto.CELO, Fiat.USD): 3,
        Pair(Crypto.CELO, Fiat.EUR): 2.4,
        Pair(Crypto.CELO, Fiat.BRL): 15,
        Pair(Stable.CUSD, Fiat.USD): 1,
        Pair(Stable.CEUR, Fiat.EUR): 1,
        Pair(Stable.CREAL, Fiat.BRL): 1
    })

# Initialize State Variables instance with default values
initial_state = StateVariables().__dict__
