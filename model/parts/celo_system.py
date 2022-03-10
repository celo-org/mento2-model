"""
Celo System
General Celo blockchain mechanisms:
* epoch rewards
"""
from model.generators.container import container
from model.generators.accounts import AccountGenerator
from model.constants import target_epoch_rewards, epoch_seconds, blocktime_seconds
from model.types import AccountType


@container.inject(AccountGenerator)
def p_epoch_rewards(_params, _substep, _state_history, prev_state,
                           account_generator=AccountGenerator):
    """
    Naively propage celo supply by adding target epoch rewards per epoch (every 17280 blocks)
    Celo epoch target rewards are rewarded linearly over the next 15 years and after
    that logarithmically. Here it's only about the next 15 linear years
    """
    if prev_state['timestep'] > 0:
        if (prev_state['timestep'] * blocktime_seconds) % epoch_seconds == 0:
            account_generator.change_account_balance(account_id=0,
                                                     delta_celo=target_epoch_rewards,
                                                     delta_cusd=0.0,
                                                     account_type=AccountType.CONTRACT)
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
