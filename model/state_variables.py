"""
Definition of State Variables, their types, and default values.
By using a dataclass to represent the State Variables:
* We can use types for Python type hints
* Set default values
* Ensure that all State Variables are initialized
"""
from typing import Dict, TypedDict
from model.entities.balance import Balance

from model.types import (
    CryptoAsset,
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


class StateVariables(TypedDict):
    """State Variables
    Each State Variable is defined as:
    state variable key: state variable type = default state variable value
    """
    floating_supply: Balance
    oracle_rate: Dict[Pair, float]
    reserve_balance: Balance
    mento_buckets: Dict[MentoExchange, MentoBuckets]
    market_buckets: MarketBuckets
    market_price: Dict[Pair, float]

# Initialize State Variables instance with default values
initial_state = StateVariables(
    floating_supply=Balance({
        CryptoAsset.CELO: CELO_SUPPLY_MEAN,
        Stable.CUSD: CUSD_SUPPLY_MEAN,
        Stable.CEUR: CEUR_SUPPLY_MEAN,
        Stable.CREAL: CREAL_SUPPLY_MEAN,
    }),
    oracle_rate={
        Pair(CryptoAsset.CELO, Fiat.USD): 3,
        Pair(CryptoAsset.CELO, Fiat.EUR): 2.5,
        Pair(CryptoAsset.CELO, Fiat.BRL): 15,
    },
    reserve_balance=Balance({
        CryptoAsset.CELO: 120000000.0
    }),
    # TODO initial calibration of buckets
    mento_buckets={
        MentoExchange.CUSD_CELO: MentoBuckets(stable=0, reserve_asset=0),
        MentoExchange.CEUR_CELO: MentoBuckets(stable=0, reserve_asset=0),
        MentoExchange.CREAL_CELO: MentoBuckets(stable=0, reserve_asset=0),
    },
    market_buckets={
        Fiat.USD: CUSD_SUPPLY_MEAN,
        Fiat.EUR: CEUR_SUPPLY_MEAN,
        Fiat.BRL: CREAL_SUPPLY_MEAN,
    },
    market_price={
        Pair(CryptoAsset.CELO, Fiat.USD): 3,
        Pair(CryptoAsset.CELO, Fiat.EUR): 2.4,
        Pair(CryptoAsset.CELO, Fiat.BRL): 15,
        Pair(Stable.CUSD, Fiat.USD): 1,
        Pair(Stable.CEUR, Fiat.EUR): 1,
        Pair(Stable.CREAL, Fiat.BRL): 1,
        Pair(CryptoAsset.ETH, Fiat.USD): 2000,
        Pair(CryptoAsset.BTC, Fiat.USD): 30000,
        Pair(CryptoAsset.DAI, Fiat.USD): 1,
    }
)
