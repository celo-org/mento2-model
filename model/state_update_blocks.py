"""
cadCAD model State Update Block structure, composed of Policy and State Update Functions
"""

import model.parts.buy_and_sell as buy_and_sell
import model.parts.borrow_and_repay as borrow_and_repay
import model.parts.celo_system as celo_system
from model.parts.buy_and_sell import BuyAndSellManager
from model.parts.actors import ActorManager
from model.parts.celo_system import AccountManager
from model.utils import update_from_signal

# Initialize buy_and_sell_manager and actor_manager
account_manager = AccountManager()
buy_and_sell_manager = BuyAndSellManager()
actor_manager = ActorManager()
from model.parts.actors import p_create_actors


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

state_update_block_create_random_irp = {
    "description": """
        Creates a new IRP with probability probability_of_new_irp_per_block:
    """,
    'policies': {
        'create_random_irp': borrow_and_repay.p_create_random_irp
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
        'liquidate_undercollateralized_irps': borrow_and_repay.p_liquidate_undercollateralized_irps
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
        'random_celo_usd_price_change': celo_system.p_random_celo_usd_price_change
    },
    'variables': {
        'celo_usd_price': update_from_signal('celo_usd_price')
    }
}

state_update_block_set_up_managers = {
    "description": """
        Set up managers if new parameter set is used
    """,
    'policies': {
        'create_actors': p_create_actors
    }
    # TODO: Add variables that are changed via actor creation (like floating supply etc)
}

state_update_block_all_actors_act = actor_manager.get_all_actor_state_update_blocks()

# Create state_update blocks list
# TODO: Can we do this in a way such that we only take the update blocks for the enabled features?
_state_update_blocks = [
    state_update_block_set_up_managers,
    state_update_block_periodic_mento_bucket_update,
    state_update_block_mento1_trade,
    state_update_block_create_random_irp,
    state_update_block_liquidate_undercollateralized_irps,
    state_update_block_random_celo_usd_price_change,
    state_update_block_all_actors_act
]

# Split the state update blocks into those used during the simulation_configuration (state_update_blocks)
# and those used in post-processing to calculate the system metrics (post_processing_blocks)
state_update_blocks = [
    block for block in _state_update_blocks if not block.get("post_processing", False)
]
post_processing_blocks = [
    block for block in _state_update_blocks if block.get("post_processing", False)
]
