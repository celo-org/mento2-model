"""
cadCAD model State Update Block structure, composed of Policy and State Update Functions
"""

from model.parts import accounting
import model.parts.market_prices as market_price

# from model.system_parameters import parameters
from model.parts import buy_and_sell
from model.parts import celo_system
from model.utils import update_from_signal


state_update_block_random_trading = {
    "description": """
        Single random trader
    """,
    "policies": {"random_trade": accounting.p_random_trading},
    "variables": {
        "mento_buckets": update_from_signal("mento_buckets"),
        "reserve_account": update_from_signal("reserve_account"),
        "floating_supply": update_from_signal("floating_supply"),
        "mento_rate": update_from_signal("mento_rate"),
    },
}


# according to impact timing function
state_update_block_price_impact = {
    "description": """
    """,
    "policies": {"market_price": market_price.p_price_impact},
    "variables": {
        "market_price": update_from_signal("market_price"),
        # 'virtual_tanks': update_from_signal('virtual_tanks')
    },
}

state_update_block_market_price_change = {
    "description": """
    """,
    "policies": {"market_price": market_price.p_market_price},
    "variables": {
        "market_price": update_from_signal("market_price"),
        "virtual_tanks": update_from_signal("virtual_tanks"),
    },
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

state_update_block_epoch_rewards = {
    "description": """
        epoch rewards propagation:
        * floating supply increase by epoch rewards
    """,
    'policies': {
        'target_epoch_rewards': celo_system.p_target_epoch_rewards
    },
    'variables': {
        'floating_supply': update_from_signal('floating_supply')
    }
}

# state_update_block_update_state_variables_from_generators = {
#     "description": """
#         Updates state variables from generators
#     """,
#     'policies': {
#         'state_variables_from_generators': buy_and_sell.p_state_variables_from_generators
#     },
#     'variables': {
#         'reserve_balance': update_from_signal('reserve_balance'),
#         'floating_supply': update_from_signal('floating_supply')
#     }
# }

# Create state_update blocks list
_state_update_blocks = [
    state_update_block_market_price_change,
    state_update_block_periodic_mento_bucket_update,
    state_update_block_random_trading,
    state_update_block_price_impact,
    state_update_block_epoch_rewards,
    #state_update_block_update_state_variables_from_generators
]



# Split the state update blocks into those used during the simulation_configuration
# and those used in post-processing to calculate the system metrics (post_processing_blocks)
state_update_blocks = [
    block for block in _state_update_blocks if not block.get("post_processing", False)
]
post_processing_blocks = [
    block for block in _state_update_blocks if block.get("post_processing", False)
]
