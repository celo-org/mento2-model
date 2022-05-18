"""
Balance class for easy balance manipulation

Balance.zero() == Balance(celo=0, cusd=0)
Balance(celo=2, cusd=10) + Balance(celo=5, cusd=0) = Balance(celo=7, cusd=10)
"""
from dataclasses import dataclass
from typing import Callable

@dataclass
class Balance:
    """
    Balance class holds various token balances and overloads
    addition and subtraction to make it easy to handle deltas.
    """
    celo: float
    cusd: float

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
        return self.celo < 0 or self.cusd < 0
