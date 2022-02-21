"""
# Mento1 related policy and state update functions

Calculation of changes in Mento buckets sizes, floating supply and reserve balances.
"""

import numpy as np
from model.constants import blocktime_seconds


def exchange(params, prev_state, sell_amount, sell_gold, min_buy_amount=0):
    spread = params['spread']
    reduced_sell_amount = sell_amount * (1 - spread)

    if sell_gold:
        buy_token_bucket = prev_state['mento_buckets']['cusd']
        sell_token_bucket = prev_state['mento_buckets']['celo']
    else:
        buy_token_bucket = prev_state['mento_buckets']['celo']
        sell_token_bucket = prev_state['mento_buckets']['cusd']

    numerator = sell_amount * (1 - spread) * buy_token_bucket
    denominator = sell_token_bucket + reduced_sell_amount
    buy_amount = numerator / denominator

    if buy_amount < min_buy_amount:
        buy_amount = np.nan

    return buy_amount


def get_random_sell_amount_in_cusd(params):
    return np.random.rand() * params['max_sell_amount']


def p_random_exchange(params, substep, state_history, prev_state):
    sell_amount = get_random_sell_amount_in_cusd(params)
    # TODO: control seed and track RN
    sell_gold = np.random.rand() > 0.5
    if sell_gold:
        sell_amount = sell_amount / prev_state['mento_rate']
    buy_amount = exchange(params, prev_state, sell_amount, sell_gold)

    if sell_gold:
        delta_cusd = -buy_amount
        delta_celo = sell_amount
    else:
        delta_cusd = sell_amount
        delta_celo = -buy_amount

    mento_buckets = {
        'cusd': prev_state['mento_buckets']['cusd'] + delta_cusd,
        'celo': prev_state['mento_buckets']['celo'] + delta_celo
    }

    floating_supply = {
        'cusd': prev_state['floating_supply']['cusd'] - delta_cusd,
        'celo': prev_state['floating_supply']['celo'] - delta_celo
    }

    reserve_account = {
        'celo': prev_state['reserve_account']['celo'] + delta_celo
    }

    mento_rate = mento_buckets['cusd'] / mento_buckets['celo']

    # market_price_generator = params['generators'].get(MarketPriceGenerator)
    # market_price = {'cusd_usd': market_price_generator.valuate(
    #    floating_supply['cusd'], virtual_tanks['usd'])}

    return {
        'mento_buckets': mento_buckets,
        'floating_supply': floating_supply,
        'reserve_account': reserve_account,
        'mento_rate': mento_rate,
    }


def p_bucket_update(params, substep, state_history, prev_state):
    """
    Only update buckets every update_frequency_seconds
    """
    if (blocktime_seconds * prev_state['timestep']) % params['bucket_update_frequency_seconds'] == 0:
        celo_bucket = params['reserve_fraction'] * prev_state['reserve_account']['celo']
        cusd_bucket = prev_state['market_price']['celo_usd'] * celo_bucket
        mento_buckets = {
            'cusd': cusd_bucket,
            'celo': celo_bucket
        }

    else:
        mento_buckets = {
            'cusd': prev_state['mento_buckets']['cusd'],
            'celo': prev_state['mento_buckets']['celo']
        }

    return {'mento_buckets': mento_buckets}
