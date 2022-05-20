"""
Celo System
General Celo blockchain mechanisms:
* epoch rewards
"""
from model.entities.balance import Balance
from model.generators.accounts import AccountGenerator
from model.constants import target_epoch_rewards_downscaled, seconds_per_epoch, blocktime_seconds
from model.utils.generator_container import inject


@inject(AccountGenerator)
def p_epoch_rewards(_params, _substep, _state_history, prev_state,
                           account_generator=AccountGenerator):
    """
    Naively propage celo supply by adding target epoch rewards per epoch (every 17280 blocks)
    Celo epoch target rewards are rewarded linearly over the next 15 years and after
    that logarithmically. Here it's only about the next 15 linear years
    """

    is_not_epoch_block = ((prev_state['timestep'] * blocktime_seconds) % seconds_per_epoch) != 0
    if is_not_epoch_block or prev_state['timestep'] == 0:
        return {
            "floating_supply": prev_state["floating_supply"],
            "reserve_balance": prev_state["reserve_balance"],
        }

    validator_rewards = 0.07 * target_epoch_rewards_downscaled
    celo_rewards = target_epoch_rewards_downscaled - validator_rewards
    validator_rewards_in_cusd = validator_rewards / prev_state["oracle_rate"]

    account_generator.reserve.balance += Balance(
        celo=validator_rewards,
        cusd=0
    )
    account_generator.untracked_floating_supply += Balance(
        celo=celo_rewards - validator_rewards,
        cusd=validator_rewards_in_cusd
    )

    return {
        "floating_supply": account_generator.floating_supply.__dict__,
        "reserve_balance": account_generator.reserve.balance.__dict__
    }
