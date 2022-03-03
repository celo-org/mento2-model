"""
Temp file for Mento
"""
import numpy as np


def get_buy_amount(sell_amount, sell_gold, params, prev_state,  min_buy_amount=0):
    """
    Making pylint happy
    """
    spread = params["spread"]
    reduced_sell_amount = sell_amount * (1 - spread)

    if sell_gold:
        buy_token_bucket = prev_state["mento_buckets"]["cusd"]
        sell_token_bucket = prev_state["mento_buckets"]["celo"]
    else:
        buy_token_bucket = prev_state["mento_buckets"]["celo"]
        sell_token_bucket = prev_state["mento_buckets"]["cusd"]

    numerator = sell_amount * (1 - spread) * buy_token_bucket
    denominator = sell_token_bucket + reduced_sell_amount
    buy_amount = numerator / denominator

    if buy_amount < min_buy_amount:
        buy_amount = np.nan

    return buy_amount


def exchange(sell_amount, sell_gold, params, _substep, _state_history, prev_state):
    """
    Making pylint happy
    """
    if sell_gold:
        sell_amount = sell_amount / prev_state["mento_rate"]

    buy_amount = get_buy_amount(sell_amount, sell_gold, params, prev_state )

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

    floating_supply = {
        "cusd": prev_state["floating_supply"]["cusd"] - delta_cusd,
        "celo": prev_state["floating_supply"]["celo"] - delta_celo,
    }

    reserve_account = {"celo": prev_state["reserve_account"]["celo"] + delta_celo}

    mento_rate = mento_buckets["cusd"] / mento_buckets["celo"]

    # market_price_generator = params['generators'].get(MarketPriceGenerator)
    # market_price = {'cusd_usd': market_price_generator.valuate(
    #    floating_supply['cusd'], virtual_tanks['usd'])}

    return (
        {
            "mento_buckets": mento_buckets,
            "floating_supply": floating_supply,
            "reserve_account": reserve_account,
            "mento_rate": mento_rate,
        },
        {"cusd": delta_cusd, "celo": delta_celo},
    )
