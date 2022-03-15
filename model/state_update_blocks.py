"""
cadCAD model State Update Block structure, composed of Policy and State Update Functions
"""
from model.utils import update_from_signal
from model.parts import policies

state_update_block_periodic_mento_bucket_update = {
    "description": """
        Updates blocks only when update bucket_update_frequency_seconds has passed since last update:
    """,
    'policies': {
        'bucket_update': policies.p_bucket_update
    },
    'variables': {
        'mento_buckets': update_from_signal('mento_buckets')
    }
}

state_update_block_create_random_irp = {
    "description": """
        Creates a new IRP with probability probability_of_new_irp_per_block:
    """,
    'policies': {
        'create_random_irp': policies.p_create_random_irp
    },
    'variables': {
        'total_celo_deposited': update_from_signal('total_celo_deposited'),
        'total_cusd_borrowed': update_from_signal('total_cusd_borrowed')
    }
}

state_update_block_liquidate_undercollateralized_irps = {
    "description": """
        Liquidates all undercollateralized IRPs:
    """,
    'policies': {
        'liquidate_undercollateralized_irps': policies.p_liquidate_undercollateralized_irps
    },
    'variables': {
        'total_celo_deposited': update_from_signal('total_celo_deposited'),
        'total_cusd_borrowed': update_from_signal('total_cusd_borrowed'),
        'total_celo_liquidated': update_from_signal('total_celo_liquidated'),
        'total_cusd_from_liquidated_irps': update_from_signal('total_cusd_from_liquidated_irps')
    }
}

state_update_block_random_celo_usd_price_change = {
    "description": """
        Create a random change in the celo_usd_price
    """,
    'policies': {
        'random_celo_usd_price_change': policies.p_random_celo_usd_price_change
    },
    'variables': {
        'celo_usd_price': update_from_signal('celo_usd_price')
    }
}

state_update_block_actors_act = {
    "description": """
        Actors acting
    """,
    'policies': {
        'p_actors_act': policies.p_actors_act
    },
    'variables': {
        'mento_buckets': update_from_signal('mento_buckets'),
        'floating_supply': update_from_signal('floating_supply'),
        'reserve_balance': update_from_signal('reserve_balance'),
        'mento_rate': update_from_signal('mento_rate')
    }
}


# Create state_update blocks list
# TODO: Can we do this in a way such that we only take the update blocks for the enabled features?
_state_update_blocks = [
    state_update_block_periodic_mento_bucket_update,
    state_update_block_random_celo_usd_price_change,
    state_update_block_create_random_irp,  # TODO: Creating and management of IRPs via actors
    state_update_block_liquidate_undercollateralized_irps,
    state_update_block_actors_act
]

# Split the state update blocks into those used during the simulation_configuration (state_update_blocks)
# and those used in post-processing to calculate the system metrics (post_processing_blocks)
state_update_blocks = [
    block for block in _state_update_blocks if not block.get("post_processing", False)
]
post_processing_blocks = [
    block for block in _state_update_blocks if block.get("post_processing", False)
]
