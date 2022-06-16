"""
cadCAD model State Update Block structure, composed of Policy and State Update Functions
"""
import logging

# from model.system_parameters import parameters
from model.generators import (
    AccountGenerator,
    OracleRateGenerator,
    MentoExchangeGenerator
)
from model.parts import celo_system
from model.parts import reserve
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
        "market_price": update_from_signal("market_price")
    },
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

state_update_block_reserve_statistics = {
    "description": """
        reserve statistics
    """,
    'policies': {
        'reserve_statistics': reserve.p_reserve_statistics
    },
    'variables': {
        'reserve_balance_in_usd': update_from_signal('reserve_balance_in_usd'),
        'reserve_ratio': update_from_signal('reserve_ratio'),
        'collateralisation_ratio': update_from_signal('collateralisation_ratio'),
        'floating_supply_stables_in_usd': update_from_signal('floating_supply_stables_in_usd')
    }
}

# Create state_update blocks list
_state_update_blocks = [
    state_update_block_market_price_change,
    generator_state_update_block(OracleRateGenerator, "report"),
    generator_state_update_block(MentoExchangeGenerator, "bucket_update"),
    generator_state_update_block(AccountGenerator, "traders"),
    state_update_block_epoch_rewards,
    state_update_block_price_impact,
    state_update_block_reserve_statistics,
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
