"""
# Celo System

General Celo blockchain mechanisms, such as updating the CELO supply through epoch rewards.
"""

from model.constants import celo_genesis_supply, celo_max_supply, epoch_seconds, blocktime_seconds

def p_target_epoch_rewards(params, substep, state_history, prev_state):
    """
    Naively propage celo supply by adding target epoch rewards per epoch (every 17280 blocks)
    Celo epoch target rewards are rewarded linearly over the next 15 years and after that logarithmically.
    Here it's only about the next 15 linear years
    """
    if prev_state['timestep'] > 0:
        if (prev_state['timestep'] * blocktime_seconds) % epoch_seconds == 0:
            celo_total_epoch_rewards = celo_max_supply - celo_genesis_supply
            celo_linear_total_epoch_rewards = celo_total_epoch_rewards / 2
            target_epoch_rewards = celo_linear_total_epoch_rewards / 15 / 365

            floating_supply = {
                'cusd': prev_state['floating_supply']['cusd'],
                'celo': prev_state['floating_supply']['celo'] + target_epoch_rewards
            }
        else:
            floating_supply = {
                'cusd': prev_state['floating_supply']['cusd'],
                'celo': prev_state['floating_supply']['celo']
            }
    else:
        floating_supply = {
            'cusd': prev_state['floating_supply']['cusd'],
            'celo': prev_state['floating_supply']['celo']
        }

    return {
        'floating_supply': floating_supply,
    }