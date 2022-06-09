"""
Balance class for easy balance manipulation

Balance.zero() == Balance(celo=0, cusd=0)
Balance(celo=2, cusd=10) + Balance(celo=5, cusd=0) = Balance(celo=7, cusd=10)
"""
from typing import Callable, Dict, TYPE_CHECKING

from model.types import CryptoAsset, Fiat, Pair
from model.utils.exchange_rates import get_exchange_rate
if TYPE_CHECKING:
    from model.types import Currency


class Balance(dict):
    """
    Balance class holds various token balances and overloads
    addition and subtraction to make it easy to handle deltas.
    """
    values: Dict["Currency", float]

    def __init__(self, initial_values: Dict["Currency", float] = None):
        super().__init__()
        self.update(initial_values or {})

    def __str__(self) -> str:
        values = ", ".join([
            f"{currency}: {value}"
            for (currency, value) in self.items()
        ])
        return f"Balance({values})"

    @staticmethod
    def zero():
        return Balance()

    def __add__(self, other: "Balance"):
        return self.__combine__(other, lambda a, b: a + b)

    def __sub__(self, other: "Balance"):
        return self.__combine__(other, lambda a, b: a - b)

    def __combine__(self, other: "Balance", combinator: Callable[[int, int], int]):
        return Balance({
            currency: combinator(self.get(currency, 0), other.get(currency, 0))
            for currency in set(self.keys()).union(other.keys())
        })

    def values_in_usd(self, market_prices: Dict[Pair, float]):
        values_in_usd = {
            key: inventory * market_prices.get(Pair(key, Fiat.USD))
            if isinstance(key, CryptoAsset)
            else inventory * get_exchange_rate(
                market_prices=market_prices,
                base=key, quote=Fiat.USD
            )
            for key, inventory in self.items()}
        return values_in_usd

    @property
    def any_negative(self) -> bool:
        for (_, value) in self.items():
            if value < 0:
                return True
        return False
