"""
Balance class for easy balance manipulation

Balance.zero() == Balance(celo=0, cusd=0)
Balance(celo=2, cusd=10) + Balance(celo=5, cusd=0) = Balance(celo=7, cusd=10)
"""
from typing import Callable, TYPE_CHECKING, Dict
if TYPE_CHECKING:
    from model.types import Currency

class Balance:
    """
    Balance class holds various token balances and overloads
    addition and subtraction to make it easy to handle deltas.
    """
    values: Dict["Currency", float]

    def __init__(self, initial_values: Dict["Currency", float] = None):
        self.values = initial_values or {}

    def get(self, currency: "Currency") -> float:
        return self.values.get(currency, 0)

    def set(self, currency: "Currency", value: float):
        self.values[currency] = value

    def __str__(self) -> str:
        values = ", ".join([
            f"{currency}: {value}"
            for (currency, value) in self.values.items()
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
            currency: combinator(self.get(currency), other.get(currency))
            for currency in set(self.values.keys()).union(other.values.keys())
        })

    @property
    def any_negative(self) -> bool:
        for (_, value) in self.values.items():
            if value < 0:
                return True
        return False
