"""
Definition of State Variables, their types, and default values.

By using a dataclass to represent the State Variables:
* We can use types for Python type hints
* Set default values
* Ensure that all State Variables are initialized
"""


from dataclasses import dataclass, fields
from datetime import datetime

import model.constants as constants
import data.api.beaconchain as beaconchain
import data.api.celo_explorer as etherscan
from model.system_parameters import validator_environments
from model.types import (
    CELO,
    CUSD,
    Stage,
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


# Get number of validator environments for initializing Numpy array size
number_of_validator_environments = len(validator_environments)

# Initial state from external live data source, setting a default in case API call fails
number_of_active_validators: int = beaconchain.get_validators_count(default=156_250)
eth_staked: CELO = (
    beaconchain.get_total_validator_balance(default=5_000_000e9) / constants.gwei
)
eth_supply: CELO = etherscan.get_eth_supply(default=116_250_000e18) / constants.wei


@dataclass
class StateVariables:
    """State Variables
    Each State Variable is defined as:
    state variable key: state variable type = default state variable value
    """

    # Time state variables
    stage: Stage = None
    """
    The stage of the Mento1.0 to Mento2.0 upgrade process.

    See "stage" System Parameter in model.system_parameters
    & model.types.Stage Enum for further documentation.
    """
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
