"""
cadCAD model State Update Block structure, composed of Policy and State Update Functions
"""

import model.parts.mento1 as mento1
import model.parts.celo_system as celo_system
from model.system_parameters import parameters
from model.utils import update_from_signal

state_update_block_target_epoch_rewards = {
    "description": """
        epoch rewards propagation:
        * floating supply increase by epoch rewards
    """,
    'policies': {
        'target_epoch_rewards': celo_system.p_target_epoch_rewards
    },
    'variables': {
        'floating_supply': update_from_signal('floating_supply'),
    }
}

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
        'reserve_account': update_from_signal('reserve_account'),
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

# Conditionally update the order of the State Update Blocks using a ternary operator
_state_update_blocks = (
    # Structure state update blocks as follows:
    [
        state_update_block_periodic_mento_bucket_update,
        state_update_block_mento1_trade,
        state_update_block_target_epoch_rewards,
    ]
)

# Split the state update blocks into those used during the simulation_configuration (state_update_blocks)
# and those used in post-processing to calculate the system metrics (post_processing_blocks)
state_update_blocks = [
    block for block in _state_update_blocks if not block.get("post_processing", False)
]
post_processing_blocks = [
    block for block in _state_update_blocks if block.get("post_processing", False)
]
