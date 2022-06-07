"""
Reserve metric and advanced balance calculation
"""

from model.types import (
    CryptoAsset,
    Fiat,
    Pair,
    Stable
)


def p_reserve_statistics(
    _params,
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

    stable_fiat_pairs = [[_params['mento_exchanges_config'][exchange].stable,
                          _params['mento_exchanges_config'][exchange].peg]
                         for exchange in _params['mento_exchanges_config']]

    stable_fiat_pairs = dict(zip([pair[0] for pair in stable_fiat_pairs],
                                 [pair[1] for pair in stable_fiat_pairs]))

    # outstanding stables in Fiat.USD
    stables_balance = sum([prev_state['floating_supply'].get(stable)
                           * prev_state['market_price'].get(Pair(stable,
                                                                 stable_fiat_pairs.get(stable)))
                           / exchange_rates.get(Pair(Fiat.USD, stable_fiat_pairs.get(stable)))
                           for stable in Stable])

    reserve_ratio = reserve_balance / stables_balance

    return {
        'reserve_balance_in_usd': reserve_balance,
        'floating_supply_stables_in_usd': stables_balance,
        'reserve_ratio': reserve_ratio
    }
