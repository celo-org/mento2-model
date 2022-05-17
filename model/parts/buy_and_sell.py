"""
Buy and sell (Mento1) related policy and state update functions
"""
import numpy as np
from model.constants import blocktime_seconds

# raise numpy warnings as errors
np.seterr(all='raise')


def p_bucket_update(
    params,
    _substep,
    _state_history,
    prev_state,
):
    """
    Policy function which updates buckets every update_frequency_seconds
    """
    update_required = buckets_should_be_reset(
        params=params, prev_state=prev_state
    )
    if update_required:
        mento_buckets = bucket_update(
            params=params, prev_state=prev_state
        )
    else:
        mento_buckets = {'mento_buckets': prev_state['mento_buckets']}
    return mento_buckets


def buckets_should_be_reset(params, prev_state):
    update_required = ((blocktime_seconds * prev_state['timestep']) % params[
        'bucket_update_frequency_seconds'] == 0)
    return update_required


def bucket_update(params, prev_state):
    celo_bucket = params['reserve_fraction'] * prev_state['reserve_balance']['celo']
    cusd_bucket = prev_state['oracle_rate'] * celo_bucket
    mento_buckets = {
        'cusd': cusd_bucket,
        'celo': celo_bucket
    }
    return {'mento_buckets': mento_buckets}


def get_buy_amount(params, sell_amount, sell_gold, prev_state,  min_buy_amount=0):
    """
    Making pylint happy
    """
    reduced_sell_amount = sell_amount * (1 - params["spread"])

    if sell_gold:
        buy_token_bucket = prev_state["mento_buckets"]["cusd"]
        sell_token_bucket = prev_state["mento_buckets"]["celo"]
    else:
        buy_token_bucket = prev_state["mento_buckets"]["celo"]
        sell_token_bucket = prev_state["mento_buckets"]["cusd"]

    numerator = sell_amount * (1 - params["spread"]) * buy_token_bucket
    denominator = sell_token_bucket + reduced_sell_amount
    buy_amount = numerator / denominator

    if buy_amount < min_buy_amount:
        buy_amount = np.nan

    return buy_amount


def exchange(params, sell_amount, sell_gold, _substep, _state_history, prev_state):
    """
    Update the simulation state with a trade between CELO And cUSD
    """
    buy_amount = get_buy_amount(params, sell_amount, sell_gold, prev_state)

    if sell_gold:
        delta_cusd = -buy_amount
        delta_celo = sell_amount
    else:
        delta_cusd = sell_amount
        delta_celo = -buy_amount

    mento_buckets = {
        "cusd": prev_state["mento_buckets"]["cusd"] + delta_cusd,
        "celo": prev_state["mento_buckets"]["celo"] + delta_celo,
    }

    # floating_supply = {
    #     "cusd": prev_state["floating_supply"]["cusd"] - delta_cusd,
    #     "celo": prev_state["floating_supply"]["celo"] - delta_celo,
    # }

    # reserve_balance = {"celo": prev_state["reserve_balance"]["celo"] + delta_celo}
    # accounts.reserve += delta


   # oracle_rate = mento_buckets["cusd"] / mento_buckets["celo"]
    return (
        mento_buckets,
        # {
        #     "mento_buckets": mento_buckets,
        #     "floating_supply": accounts.floating_supply,
        #     "reserve_balance": accounts.reserve
        # },
        {"cusd": delta_cusd, "celo": delta_celo},
    )
