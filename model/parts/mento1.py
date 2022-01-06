"""
# Mento1 related policy and state update functions

Calculation of changes in Mento buckets sizes, floating supply and reserve balances.
"""

import typing


def exchange(params, prev_state, sell_amount, sell_gold, min_buy_amount=0):
    spread = params['spread']
    reduced_sell_amount = sell_amount * (1 - spread)

    if sell_gold:
        buy_token_bucket = prev_state['mento_buckets']['cusd_bucket']
        sell_token_bucket = prev_state['mento_buckets']['celo_bucket']
    else:
        buy_token_bucket = prev_state['mento_buckets']['cusd_bucket']
        sell_token_bucket = prev_state['mento_buckets']['celo_bucket']

    numerator = sell_amount * (1 - spread) * buy_token_bucket
    denominator = sell_token_bucket + reduced_sell_amount
    buy_amount = numerator / denominator

    if buy_amount < min_buy_amount:
        buy_amount = np.nan

    return buy_amount


def get_random_sell_amount(params):
    return np.random.rand() * params['max_sell_amount']


def p_exchange(params, substep, state_history, prev_state):
    sell_amount = get_random_sell_amount(params)
    sell_gold = np.random.rand() > 0.5
    buy_amount = exchange(params, prev_state, sell_amount, sell_gold)

    if sell_gold:
        mento_bucket_deltas = {
            'delta_cusd': -buy_amount,
            'delta_celo': sell_amount
        }
    else:
        mento_bucket_deltas = {
            'delta_cusd': sell_amount,
            'delta_celo': -buy_amount
        }
    return {'mento_bucket_deltas': mento_bucket_deltas}


def p_bucket_update(params, substep, state_history, prev_state):
    if (params['block_time_seconds'] * prev_state['timestep']) % params['update_frequency_seconds'] == 0:
        celo_bucket = params['reserve_fraction'] * prev_state['reserve_assets']['celo']
        cusd_bucket = prev_state['mento_price'] * celo_bucket
        mento_bucket_deltas = {
            'delta_cusd': cusd_bucket - prev_state['mento_buckets']['cusd_bucket'],
            'delta_celo': celo_bucket - prev_state['mento_buckets']['celo_bucket']
        }

    else:
        mento_bucket_deltas = {
            'delta_cusd': 0,
            'delta_celo': 0
        }

    return {'mento_bucket_deltas': mento_bucket_deltas}


def s_mento_buckets(params, substep, state_history, prev_state, policy_input):
    updated_mento_bucket_cusd = prev_state['mento_buckets']['cusd_bucket'] + policy_input['mento_bucket_deltas'][
        'delta_cusd']
    updated_mento_bucket_celo = prev_state['mento_buckets']['celo_bucket'] + policy_input['mento_bucket_deltas'][
        'delta_celo']

    return 'mento_buckets', {
        'cusd_bucket': updated_mento_bucket_cusd,
        'celo_bucket': updated_mento_bucket_celo
    }


def s_reserve_assets(params, substep, state_history, prev_state, policy_input):
    updated_reserve_celo = prev_state['reserve_assets']['celo'] + policy_input['mento_bucket_deltas']['delta_celo']

    return 'reserve_assets', {
        'celo': updated_reserve_celo,
    }


def s_floating_supply(params, substep, state_history, prev_state, policy_input) -> \
        typing.TypedDict[str, typing.TypedDict]:
    updated_supply_celo = prev_state['floating_supply']['celo'] - policy_input['mento_bucket_deltas']['delta_celo']
    updated_supply_cusd = prev_state['floating_supply']['cusd'] - policy_input['mento_bucket_deltas']['delta_cusd']

    return 'floating_supply', {
        'celo': updated_supply_celo,
        'cusd': updated_supply_cusd
    }


def s_mento_price(params, substep, state_history, prev_state, policy_input):
    return 'mento_price', prev_state['mento_buckets']['cusd_bucket'] / prev_state['mento_buckets']['celo_bucket']
