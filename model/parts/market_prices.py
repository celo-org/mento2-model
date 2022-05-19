"""
# Market Price related Update and Policy functions


"""
from model.generators.markets import MarketPriceGenerator
from model.utils.generator_container import inject


@inject(MarketPriceGenerator)
def p_market_price(
    _params,
    _substep,
    _state_history,
    prev_state,
    market_price_generator: MarketPriceGenerator,
):
    """
    Provides a market price environment
    """
    market_price = market_price_generator.market_price(prev_state)
    market_buckets = {
        "usd": prev_state["floating_supply"]["cusd"] * market_price["cusd_usd"]
    }
    return {
        "market_price": market_price,
        "market_buckets": market_buckets,
        "oracle_rate": market_price["celo_usd"],
    }


@inject(MarketPriceGenerator)
def p_price_impact(
    params,
    _substep,
    state_history,
    prev_state,
    market_price_generator: MarketPriceGenerator,
):
    """
    This function adds the delayed accumulated supply of the
    current step to the floating supply needs to be applied after
    all supply changes
    """
    # TODO make this block dependent
    # TODO make sure the right step is picked
    market_price = market_price_generator.valuate_price_impact(
        floating_supply=prev_state["floating_supply"],
        pre_floating_supply=state_history[-1][-1]["floating_supply"],
        current_step=prev_state["timestep"],
        market_prices=prev_state["market_price"],
        params=params
    )

    return {"market_price": market_price}
