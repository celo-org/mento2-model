"""
cadCAD model State Update Block structure, composed of Policy and State Update Functions
"""

from model.parts import accounting
from model.parts import mento1
import model.parts.market_prices as market_price

# from model.system_parameters import parameters
from model.utils import update_from_signal

state_update_block_mento1_trade = {
    "description": """
        Single Mento1 trade:
        * Mento buckets updated
        * Reserve CELO balance updated
        * Floating supply (cUSD and CELO) updated
        * Mento price updated
    """,
    "policies": {"random_exchange": mento1.p_random_exchange},
    "variables": {
        "mento_buckets": update_from_signal("mento_buckets"),
        "reserve_account": update_from_signal("reserve_account"),
        "floating_supply": update_from_signal("floating_supply"),
        "mento_rate": update_from_signal("mento_rate"),
    },
}

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
        * Mento1 buckets updated
    """,
    "policies": {"bucket_update": mento1.p_bucket_update},
    "variables": {"mento_buckets": update_from_signal("mento_buckets")},
}

# state_update_account_update = {
#     "description": """

#     """,
#     "policies": {"acounts": accounting.p_create_accounts},
#     "variables": {"number_of_accounts": update_from_signal("number_of_accounts")},
# }


# Conditionally update the order of the State Update Blocks using a ternary operator
_state_update_blocks = (
    # Structure state update blocks as follows:
    [  # state_update_account_update,
        state_update_block_periodic_mento_bucket_update,
        state_update_block_random_trading,
        state_update_block_price_impact,
        state_update_block_market_price_change,
    ]
)

# Split the state update blocks into those used during the simulation_configuration
#  (state_update_blocks) and those used in post-processing to calculate the system
#  metrics (post_processing_blocks)
state_update_blocks = [
    block for block in _state_update_blocks if not block.get("post_processing", False)
]
post_processing_blocks = [
    block for block in _state_update_blocks if block.get("post_processing", False)
]
