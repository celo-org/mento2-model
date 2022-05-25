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
    CurrencyRate,
    Fiat,
    MentoBuckets,
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

    oracle_rate: CurrencyRate = default({
        Crypto.CELO: {
            Stable.CUSD: 3,
            Stable.CEUR: 3,
            Stable.CREAL: 3,
        }
    })

    # Reserve state variable
    reserve_balance: Dict[Crypto, float] = default({
        Crypto.CELO: 120000000.0
    })
    # Mento state variables
    # TODO initial calibration of buckets
    mento_buckets: Dict[Stable, MentoBuckets] = default({
        Stable.CUSD: MentoBuckets(0, 0),
        Stable.CEUR: MentoBuckets(0, 0),
        Stable.CREAL: MentoBuckets(0, 0)
    })


    # Virtual Market Fiat Bucket
    market_buckets: MarketBuckets = default({
        Fiat.USD: CUSD_SUPPLY_MEAN,
        Fiat.EUR: CEUR_SUPPLY_MEAN,
        Fiat.BRL: CREAL_SUPPLY_MEAN,
    })

    market_price: CurrencyRate = default({
        Crypto.CELO: {
            Fiat.USD: 3,
            Fiat.EUR: 3,
            Fiat.BRL: 3,
        },
        Stable.CUSD: {
            Fiat.USD: 1
        },
        Stable.CEUR: {
            Fiat.EUR: 1
        },
        Stable.CREAL: {
            Fiat.BRL: 1
        },
    })

# Initialize State Variables instance with default values
initial_state = StateVariables().__dict__
