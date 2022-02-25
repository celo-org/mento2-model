"""
cadCAD model State Update Block structure, composed of Policy and State Update Functions
"""

import model.parts.buy_and_sell as buy_and_sell
import model.parts.celo_system as celo_system
from model.utils import update_from_signal

state_update_block_mento1_trade = {
    "description": """
        Single Mento1 trade:
    """,
    'policies': {
        'random_exchange': buy_and_sell.p_random_exchange
    },
    'variables': {
        'mento_buckets': update_from_signal('mento_buckets'),
        'reserve_balance': update_from_signal('reserve_balance'),
        'floating_supply': update_from_signal('floating_supply'),
        'mento_rate': update_from_signal('mento_rate')
    }
}

state_update_block_periodic_mento_bucket_update = {
    "description": """
        Updates blocks only when update bucket_update_frequency_seconds has passed since last update:
    """,
    'policies': {
        'bucket_update': buy_and_sell.p_bucket_update
    },
    'variables': {
        'mento_buckets': update_from_signal('mento_buckets')
    }
}

state_update_block_random_celo_usd_price_change = {
    "description": """
        Create a random change in the celo_usd_price
    """,
    'policies': {
        'random_celo_usd_price_change': celo_system.p_random_celo_usd_price_change
    },
    'variables': {
        'celo_usd_price': update_from_signal('celo_usd_price')
    }
}

state_update_block_update_state_variables_from_generators = {
    "description": """
        Updates state variables from generators
    """,
    'policies': {
        'state_variables_from_generators': buy_and_sell.p_state_variables_from_generators
    },
    'variables': {
        'reserve_balance': update_from_signal('reserve_balance'),
        'floating_supply': update_from_signal('floating_supply')
    }
}

# Create state_update blocks list
_state_update_blocks = [
    state_update_block_periodic_mento_bucket_update,
    state_update_block_mento1_trade,
    state_update_block_random_celo_usd_price_change,
    state_update_block_update_state_variables_from_generators
]

# Split the state update blocks into those used during the simulation_configuration
# and those used in post-processing to calculate the system metrics (post_processing_blocks)
state_update_blocks = [
    block for block in _state_update_blocks if not block.get("post_processing", False)
]
post_processing_blocks = [
    block for block in _state_update_blocks if block.get("post_processing", False)
]
