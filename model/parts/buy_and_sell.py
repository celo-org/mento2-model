"""
Buy and sell (Mento1) related policy and state update functions
"""
from model.generators.buy_and_sell import BuyAndSellGenerator
from model.generators.accounts import AccountGenerator
from model.generators.container import container
from model.types import AccountType


@container.inject(BuyAndSellGenerator, AccountGenerator)
def p_random_exchange(
    params,
    _substep,
    _state_history,
    prev_state,
    buy_and_sell_generator: BuyAndSellGenerator,
    account_generator=AccountGenerator,
):
    """
    policy function to execute a random exchange
    """
    random_trade = buy_and_sell_generator.create_random_trade(
        params=params, prev_state=prev_state
    )

    state_variables_after_trade = buy_and_sell_generator.state_after_trade(
        prev_state=prev_state, trade=random_trade, account_generator=account_generator
    )

    return state_variables_after_trade


@container.inject(BuyAndSellGenerator)
def p_bucket_update(
    params,
    _substep,
    _state_history,
    prev_state,
    buy_and_sell_generator: BuyAndSellGenerator
):
    """
    Policy function which updates buckets every update_frequency_seconds
    """
    update_required = buy_and_sell_generator.buckets_should_be_reset(
        params=params, prev_state=prev_state
    )
    if update_required:
        mento_buckets = buy_and_sell_generator.bucket_update(
            params=params, prev_state=prev_state
        )
    else:
        mento_buckets = {'mento_buckets': prev_state['mento_buckets']}
    return mento_buckets


@container.inject(AccountGenerator)
def p_state_variables_from_generators(_params, _substep, _state_history, _prev_state,
                    account_generator: AccountGenerator):
    """
    Policy function which updates state variables from generator objects
    """
    floating_supply = {
        'celo': account_generator.floating_supply_celo,
        'cusd': account_generator.floating_supply_cusd
    }
    reserve_balance = {
        'celo': account_generator.get_account(account_id=0,
                                              account_type=AccountType.CONTRACT).balance["celo"],
        'cusd':  account_generator.get_account(account_id=0,
                                               account_type=AccountType.CONTRACT).balance["celo"],
    }

    return {
        'reserve_balance': reserve_balance,
        'floating_supply': floating_supply
    }
