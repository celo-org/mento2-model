"""
Calculates exchange rates between currencies
"""
from typing import Dict
from model.types import Fiat, Pair, CryptoAsset


def get_exchange_rate(market_prices: Dict, from_fiat: Fiat, to_fiat: Fiat) -> Dict[Pair, float]:
    """
    calculate specified exchange rate
    :return: exchange rate
    """
    exchange_rate = dict([
        [Pair(base=to_fiat, quote=from_fiat),
         market_prices[Pair(base=CryptoAsset.CELO, quote=from_fiat)] /
         market_prices[Pair(base=CryptoAsset.CELO,  quote=to_fiat)]]
    ])
    return exchange_rate


def get_stable_balance_in_usd(floating_supply: Dict,
                              market_prices: Dict,
                              exchanges_config: [Dict]) -> Dict[Pair, float]:
    """
    get stablecoin balance in Fiat.USD
    """
    balance = sum([floating_supply.get(config.stable) /
                   get_exchange_rate(market_prices,
                                     from_fiat=config.reference_fiat,
                                     to_fiat=Fiat.USD)[Pair(base=Fiat.USD,
                                                            quote=config.reference_fiat)]
                   for (_, config) in exchanges_config.items()
                   ])
    return balance
