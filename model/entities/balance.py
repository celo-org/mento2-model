"""
Balance class for easy balance manipulation

Balance.zero() == Balance(celo=0, cusd=0)
Balance(celo=2, cusd=10) + Balance(celo=5, cusd=0) = Balance(celo=7, cusd=10)
"""
from dataclasses import dataclass
from typing import Callable
from model.types import Currency

from model.utils import default

@dataclass
class Balance:
    """
    Balance class holds various token balances and overloads
    addition and subtraction to make it easy to handle deltas.
    """
    celo: float = default(0)
    btc: float = default(0)
    dai: float = default(0)
    eth: float = default(0)
    cusd: float = default(0)
    ceur: float = default(0)
    creal: float = default(0)

    def get(self, currency: Currency) -> float:
        return getattr(self, currency.value)

    def set(self, currency: Currency, value: float):
        if currency.value not in self.__dict__:
            raise ValueError(f"{currency.value} not a valid balance item")
        setattr(self, currency.value, value)

    @staticmethod
    def zero():
        return Balance(celo=0, cusd=0)

    def __add__(self, other: "Balance"):
        return self.__combine__(other, lambda a, b: a + b)

    def __sub__(self, other: "Balance"):
        return self.__combine__(other, lambda a, b: a - b)

    def __combine__(self, other: "Balance", combinator: Callable[[int, int], int]):
        result = Balance.zero()
        for (currency, _) in self.__dict__.items():
            setattr(result, currency, combinator(getattr(self, currency), getattr(other, currency)))
        return result

    @property
    def any_negative(self) -> bool:
        for (currency, _) in self.__dict__.items():
            if getattr(self, currency) < 0:
                return True
        return False
