"""
Celo System
General Celo blockchain mechanisms:
* epoch rewards
"""
from model.generators.container import container
from model.parts import buy_and_sell
from model.generators.accounts import AccountGenerator
from model.constants import target_epoch_rewards_downscaled, seconds_per_epoch, blocktime_seconds
from model.types import AccountType


@container.inject(AccountGenerator)
def p_epoch_rewards(params, substep, state_history, prev_state, account_generator=AccountGenerator):
    """
    Naively propage celo supply by adding target epoch rewards per epoch (every 17280 blocks)
    Celo epoch target rewards are rewarded linearly over the next 15 years and after
    that logarithmically. Here it's only about the next 15 linear years
    """
    if prev_state['timestep'] > 0:
        if (prev_state['timestep'] * blocktime_seconds) % seconds_per_epoch == 0:
            # trade validator rewards (~7% of all rewards, simplified) into cUSD
            validator_rewards = 0.07 * target_epoch_rewards_downscaled
            celo_rewards = target_epoch_rewards_downscaled - validator_rewards

            states, deltas = buy_and_sell.exchange(params=params,
                                                   sell_amount=validator_rewards,
                                                   sell_gold=True,
                                                   _substep=substep,
                                                   _state_history=state_history,
                                                   prev_state=prev_state)

            account_generator.change_account_balance(account_id=0,
                                                     delta_celo=celo_rewards - deltas["celo"],
                                                     delta_cusd=-deltas["cusd"],
                                                     account_type=AccountType.CONTRACT)

            # add celo epoch rewards to state from exchange event
            states["floating_supply"]["celo"] = states["floating_supply"]["celo"] + celo_rewards

            return states
    return {
        "mento_buckets": prev_state["mento_buckets"],
        "floating_supply": prev_state["floating_supply"],
        "reserve_balance": prev_state["reserve_balance"],
        "mento_rate": prev_state["mento_rate"],
    }
