"""
Buy and sell (Mento1) related policy and state update functions
"""
from model.generators.buy_and_sell import BuyAndSellGenerator
from model.generators.container import container


@container.inject(BuyAndSellGenerator)
def p_random_exchange(params, _substep, _state_history, prev_state,
                      buy_and_sell_generator: BuyAndSellGenerator):
    """
    policy function to execute a random exchange
    """
    random_trade = buy_and_sell_generator.create_random_trade(
        params=params,
        prev_state=prev_state
    )

    state_variables_after_trade = buy_and_sell_generator.state_after_trade(
        prev_state=prev_state,
        trade=random_trade,
    )

    return state_variables_after_trade


@container.inject(BuyAndSellGenerator)
def p_bucket_update(params, _substep, _state_history, prev_state,
                    buy_and_sell_generator: BuyAndSellGenerator):
    """
    Policy function which updates buckets every update_frequency_seconds
    """
    if buy_and_sell_generator.buckets_should_be_reset(params=params, prev_state=prev_state):
        return buy_and_sell_generator.reset_buckets(params=params, prev_state=prev_state)
    return None
