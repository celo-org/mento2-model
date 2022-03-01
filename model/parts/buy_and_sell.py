"""
Buy and sell (Mento1) related policy and state update functions
"""
from model.generators.buy_and_sell import BuyAndSellGenerator
from model.generators.accounts import AccountGenerator
from model.generators.container import container


@container.inject(BuyAndSellGenerator, AccountGenerator)
def p_random_exchange(params, _substep, _state_history, prev_state,
                      buy_and_sell_generator: BuyAndSellGenerator,
                      account_generator=AccountGenerator):
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
        account_generator=account_generator
    )

    return state_variables_after_trade


@container.inject(BuyAndSellGenerator, AccountGenerator)
def p_bucket_update(params, _substep, _state_history, prev_state,
                    buy_and_sell_generator: BuyAndSellGenerator,
                    account_generator: AccountGenerator):
    """
    Policy function which updates buckets every update_frequency_seconds
    """
    if buy_and_sell_generator.buckets_should_be_reset(params=params,
                                                      prev_state=prev_state):
        return buy_and_sell_generator.reset_buckets(params=params,
                                                    prev_state=prev_state,
                                                    account_generator=account_generator)
    return None


# @container.inject(AccountGenerator)
# def p_state_variables_from_generators(_params, _substep, _state_history, _prev_state,
#                     account_generator: AccountGenerator):
#     """
#     Policy function which updates state variables from generator objects
#     """
#     floating_supply: {
#         'celo': account_generator.floating_supply_celo,
#         'cusd': account_generator.floating_supply_cusd
#     }
#     reserve_balance: {
#         'celo': account_generator.get_account(0)['celo'],
#         'cusd': account_generator.get_account(0)['cusd']
#     }

#     return {
#         'reserve_balance': reserve_balance,
#         'floating_supply': floating_supply
#     }
