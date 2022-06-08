"""
Reserve metric and advanced balance calculation
"""

from model.types import (
    CryptoAsset,
    Fiat,
    Pair
)


def p_reserve_statistics(
    params,
    _substep,
    _state_history,
    prev_state,
):
    """
    calculates reserve statistics
    """
    exchange_rates = {
        Pair(Fiat.USD, Fiat.USD): 1,
        Pair(Fiat.USD, Fiat.EUR): prev_state['market_price'][Pair(CryptoAsset.CELO, Fiat.EUR)]
                                  / prev_state['market_price'][Pair(CryptoAsset.CELO, Fiat.USD)],
        Pair(Fiat.USD, Fiat.BRL): prev_state['market_price'][Pair(CryptoAsset.CELO, Fiat.BRL)]
                                  /prev_state['market_price'][Pair(CryptoAsset.CELO, Fiat.USD)]
                      }

    # reserve balance in Fiat.USD
    reserve_balance = sum([inventory * prev_state['market_price'].get(Pair(key, Fiat.USD))
                           for key, inventory in prev_state['reserve_balance'].items()])

    # outstanding stables in Fiat.USD
    stables_balance = sum([
        prev_state['floating_supply'].get(config.stable)
        * prev_state['market_price'].get(Pair(config.stable, config.reference_fiat))
        / exchange_rates.get(Pair(Fiat.USD, config.reference_fiat))
        for (_, config) in params['mento_exchanges_config'].items()
    ])

    reserve_ratio = reserve_balance / stables_balance

    return {
        'reserve_balance_in_usd': reserve_balance,
        'floating_supply_stables_in_usd': stables_balance,
        'reserve_ratio': reserve_ratio
    }
