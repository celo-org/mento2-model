"""
# Market Price related Update and Policy functions


"""


from sklearn.random_projection import SparseRandomProjection
from model.types import VirtualTanks


def p_market_price(params, substep, state_history, prev_state):
    market_price = {
        'cusd_usd':  prev_state['_market_price_generator'].market_price(prev_state)}
    virtual_tanks = {'usd': prev_state['floating_supply']
                     ['cusd'] * market_price['cusd_usd']}
    return {'market_price': market_price,
            'virtual_tanks': virtual_tanks}


def p_effective_supply(params, substep, state_history, prev_state):
    """
    This function adds the delayed accumulated supply of the current step to the floating supply
    """
    temp = prev_state['floating_supply']['cusd'] - \
        state_history[-1][-1]['floating_supply']['cusd']

    # _market_price_generator'].valuate_price_impact()
    return {'effective_supply': {'cusd': None}}


def p_market_price_impact(params, substep, state_history, prev_state):
    """
    This function calculates the new market price based on the additional supply from p_supply_release
    can be combined in one function
    """
    prev_state['_market_price_generator'].valuate(
        prev_state['floating_supply'], prev_state['virtual_tanks']['usd'])
