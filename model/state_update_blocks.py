"""
cadCAD model State Update Block structure, composed of Policy and State Update Functions
"""
import logging

# from model.system_parameters import parameters
from model.generators.accounts import AccountGenerator
from model.parts import buy_and_sell
from model.parts import celo_system
import model.parts.market_prices as market_price
from model.utils import update_from_signal
from model.utils.generator import generator_state_update_block

# according to impact timing function
state_update_block_price_impact = {
    "description": """
        state_update_block_price_impact has to be the last update in a block,
        as it is responsible for calculating the price changes due to all supply
        changes in this block
    """,
    "policies": {"market_price": market_price.p_price_impact},
    "variables": {
        "market_price": update_from_signal("market_price"),
        # 'market_buckets': update_from_signal('market_buckets')
    },
}

state_update_block_market_price_change = {
    "description": """
        state_update_block_price_change has to be the last update in a block,
        as it is responsible for calculating the price changes due to all supply
        changes in this block
    """,
    "policies": {"market_price": market_price.p_market_price},
    "variables": {
        "market_price": update_from_signal("market_price"),
        "market_buckets": update_from_signal("market_buckets"),
        "oracle_rate": update_from_signal("oracle_rate")
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
        'target_epoch_rewards': celo_system.p_epoch_rewards
    },
    'variables': {
        'floating_supply': update_from_signal('floating_supply'),
        "reserve_balance": update_from_signal("reserve_balance")
    }
}

# Create state_update blocks list
_state_update_blocks = [
    state_update_block_market_price_change,
    state_update_block_periodic_mento_bucket_update,
    generator_state_update_block(AccountGenerator, "traders"),
    state_update_block_epoch_rewards,
    # generator_state_update_block(AccountGenerator, "checkpoint"),
    state_update_block_price_impact,
]

price_impact_not_last = (state_update_block_price_impact in _state_update_blocks) and (
    _state_update_blocks[-1] is not state_update_block_price_impact
)
# force state_update_block_price_impact to be last substep
if price_impact_not_last:
    _state_update_blocks.append(
        _state_update_blocks.pop(
            _state_update_blocks.index(state_update_block_price_impact)
        )
    )
    logging.info("state_update_block_price_impact reassigned to last substep")

# Split the state update blocks into those used during the simulation_configuration
# and those used in post-processing to calculate the system metrics (post_processing_blocks)
state_update_blocks = [
    block for block in _state_update_blocks if not block.get("post_processing", False)
]
post_processing_blocks = [
    block for block in _state_update_blocks if block.get("post_processing", False)
]
