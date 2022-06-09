"""
Reserve metric and advanced balance calculation
"""

from model.types import (
    Fiat,
    Pair
)
from model.utils.exchange_rates import get_stable_balance_in_usd


def p_reserve_statistics(
    params,
    _substep,
    _state_history,
    prev_state,
):
    """
    calculates reserve statistics
    """
    reserve_balance_usd = sum([inventory * prev_state['market_price'].get(Pair(key, Fiat.USD))
                           for key, inventory in prev_state['reserve_balance'].items()])

    stables_balance_usd = get_stable_balance_in_usd(prev_state['floating_supply'],
                                                prev_state['market_price'],
                                                params['mento_exchanges_config'])

    reserve_ratio = reserve_balance_usd / stables_balance_usd

    return {
        'reserve_balance_in_usd': reserve_balance_usd,
        'floating_supply_stables_in_usd': stables_balance_usd,
        'reserve_ratio': reserve_ratio
    }
