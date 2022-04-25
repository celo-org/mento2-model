"""
Celo System
General Celo blockchain mechanisms:
* epoch rewards
"""
from lib.generator_container import inject
from model.entities.balance import Balance
from model.generators.accounts import AccountGenerator
from model.constants import target_epoch_rewards, seconds_per_epoch, blocktime_seconds


@inject(AccountGenerator)
def p_epoch_rewards(_params, _substep, _state_history, prev_state,
                           account_generator=AccountGenerator):
    """
    Naively propage celo supply by adding target epoch rewards per epoch (every 17280 blocks)
    Celo epoch target rewards are rewarded linearly over the next 15 years and after
    that logarithmically. Here it's only about the next 15 linear years
    """
    if prev_state['timestep'] > 0:
        if (prev_state['timestep'] * blocktime_seconds) % seconds_per_epoch == 0:
            account_generator.reserve.balance += Balance(celo=target_epoch_rewards, cusd=0)
            floating_supply = {
                "cusd": prev_state["floating_supply"]["cusd"],
                "celo": prev_state["floating_supply"]["celo"] + target_epoch_rewards,
            }
            return {
                "floating_supply": floating_supply,
            }
    return {
        "floating_supply": prev_state["floating_supply"],
    }
