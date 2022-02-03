"""
# Mento1 related policy and state update functions

Calculation of changes in Mento buckets sizes, floating supply and reserve balances.
"""


from model.generators.container import container
from model.generators.markets import MarketPriceGenerator


@container.inject(MarketPriceGenerator)
def p_market_price(params, substep, state_history, prev_state, market_price_generator):
    market_price = {
        'cusd_usd': market_price_generator.market_price(prev_state)}
    return {'market_price': market_price,
            'virtual_tanks': {'usd': prev_state['virtual_tanks']['usd']}}
