"""
Celo System
General Celo blockchain mechanisms:
* epoch rewards
"""
from model.entities.balance import Balance
from model.generators.accounts import AccountGenerator
from model.constants import target_epoch_rewards_downscaled, seconds_per_epoch, blocktime_seconds
from model.utils.generator_container import inject
from model.parts import buy_and_sell


@inject(AccountGenerator)
def p_epoch_rewards(params, substep, state_history, prev_state,
                           account_generator=AccountGenerator):
    """
    Naively propage celo supply by adding target epoch rewards per epoch (every 17280 blocks)
    Celo epoch target rewards are rewarded linearly over the next 15 years and after
    that logarithmically. Here it's only about the next 15 linear years
    """

    is_not_epoch_block = ((prev_state['timestep'] * blocktime_seconds) % seconds_per_epoch) != 0
    if is_not_epoch_block or prev_state['timestep'] == 0:
        return dict(
            mento_buckets=prev_state["mento_buckets"],
            floating_supply=prev_state["floating_supply"],
            reserve_balance=prev_state["reserve_balance"],
        )

    validator_rewards = 0.07 * target_epoch_rewards_downscaled
    celo_rewards = target_epoch_rewards_downscaled - validator_rewards

    mento_buckets, deltas = buy_and_sell.exchange(params=params,
                                                  sell_amount=validator_rewards,
                                                  sell_gold=True,
                                                  _substep=substep,
                                                  _state_history=state_history,
                                                  prev_state=prev_state)

    account_generator.reserve.balance += Balance(
        celo=deltas["celo"],
        cusd=0
    )
    account_generator.untracked_floating_supply += Balance(
        celo=celo_rewards - deltas["celo"],
        cusd=deltas["cusd"]
    )

    return dict(
        mento_buckets=mento_buckets,
        floating_supply=account_generator.floating_supply.__dict__,
        reserve_balance=account_generator.reserve.balance.__dict__)
