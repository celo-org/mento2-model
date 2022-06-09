"""
Calculates exchange rates between currencies
"""
from typing import Dict
from model.types import Fiat, Pair, CryptoAsset, Stable


def get_exchange_rate(market_prices: Dict,
                      base: Stable, quote: Fiat
                      ) -> Dict[Pair, float]:
    """
    This function calculates cStable/Fiat rates where Fiat is not reference Fiat
    """
    exchange_pair = Pair(base, quote)
    if exchange_pair in market_prices:
        rate = market_prices[Pair(base, quote)]
    else:
        pair_1 = [pair for pair in market_prices if pair.base == base]
        assert len(pair_1) == 1, f'No or multiple pairs simulated for {base}'
        pair_1 = pair_1[0]
        pair_2 = Pair(CryptoAsset.CELO, pair_1.quote)
        pair_3 = Pair(CryptoAsset.CELO, quote)
        rate = market_prices[pair_1] / market_prices[pair_2] * market_prices[pair_3]

    return rate
