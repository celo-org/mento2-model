"""
# Market Price related Update and Policy functions


"""
from model.generators.container import container
from model.generators.markets import MarketPriceGenerator


@container.inject(MarketPriceGenerator)
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
    return {"market_price": market_price, "market_buckets": market_buckets}


@container.inject(MarketPriceGenerator)
def p_price_impact(
    _params,
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
        prev_state["floating_supply"],
        state_history[-1][-1]["floating_supply"],
        prev_state["market_buckets"],
        prev_state["timestep"],
    )
    return {"market_price": market_price}
