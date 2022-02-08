"""
cadCAD model State Update Block structure, composed of Policy and State Update Functions
"""

import model.parts.buy_and_sell as mento1
import model.parts.borrow_and_repay as borrow
from model.utils import update_from_signal

state_update_block_mento1_trade = {
    "description": """
        Single Mento1 trade:
        * Mento buckets updated
        * Reserve CELO balance updated
        * Floating supply (cUSD and CELO) updated
        * Mento price updated
    """,
    'policies': {
        'random_exchange': mento1.p_random_exchange
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
        * Mento1 buckets updated
    """,
    'policies': {
        'bucket_update': mento1.p_bucket_update
    },
    'variables': {
        'mento_buckets': update_from_signal('mento_buckets')
    }
}

state_update_block_create_random_irp = {
    "description": """
        Creates a new IRP with probability probability_of_new_irp_per_block:
        * Mento1 buckets updated
    """,
    'policies': {
        'create_random_irp': borrow.p_create_random_irp
    },
    'variables': {
        'total_celo_lend': update_from_signal('total_celo_lend'),
        'total_cusd_borrowed': update_from_signal('total_cusd_borrowed')
    }
}

# Create state_update blocks list
# TODO: Can we do this in a way such that we only take the update blocks for the enabled features?
_state_update_blocks = [
    state_update_block_periodic_mento_bucket_update,
    state_update_block_mento1_trade,
    state_update_block_create_random_irp
]

# Split the state update blocks into those used during the simulation_configuration (state_update_blocks)
# and those used in post-processing to calculate the system metrics (post_processing_blocks)
state_update_blocks = [
    block for block in _state_update_blocks if not block.get("post_processing", False)
]
post_processing_blocks = [
    block for block in _state_update_blocks if block.get("post_processing", False)
]
