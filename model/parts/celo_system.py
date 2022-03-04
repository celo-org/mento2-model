"""
Celo System

General Celo blockchain mechanisms, such as account management andepoch rewards
"""
import numpy as np

def p_random_celo_usd_price_change(_params, _substep, _state_history, prev_state):
    """
    Create some random changes in celo_usd_price
    """
    vola_per_block = 5.0 / np.sqrt(365*24*60*12)  # Annual vola of 500% for some action
    pct_change = np.random.normal() * vola_per_block
    return {
        'celo_usd_price': prev_state['celo_usd_price'] * np.exp(pct_change)
    }
