"""
# Market Price related Update and Policy functions


"""
import logging
import time
from sklearn.random_projection import SparseRandomProjection
from model.types import VirtualTanks
from model.generators.container import container
from model.generators.markets import MarketPriceGenerator


@container.inject(MarketPriceGenerator)
def p_market_price(params, substep, state_history, prev_state, market_price_generator: MarketPriceGenerator):
    market_price = market_price_generator.market_price(prev_state)
    virtual_tanks = {'usd': prev_state['floating_supply']
                     ['cusd'] * market_price['cusd_usd']}
    return {'market_price': market_price,
            'virtual_tanks': virtual_tanks}


@container.inject(MarketPriceGenerator)
def p_price_impact(params, substep, state_history, prev_state, market_price_generator: MarketPriceGenerator):
    """
    This function adds the delayed accumulated supply of the current step to the floating supply
    needs to be applied after all supply changes
    """
    # TODO make this block dependent
    # TODO make sure the right step is picked
    market_price = market_price_generator.valuate_price_impact(prev_state['floating_supply'],
                                                               state_history[-1][-1]['floating_supply'],
                                                               prev_state['virtual_tanks'],
                                                               prev_state['timestep'])
    # market_price_generator.valuate_price_impact()

    return {'market_price':  market_price}
