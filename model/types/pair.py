"""
Provides a Pair class with exchange rate functionality
"""
from __future__ import annotations
from typing import TYPE_CHECKING, NamedTuple, Union
from model.types.base import CryptoAsset, Currency, Fiat, Stable

if TYPE_CHECKING:
    from model.state_variables import StateVariables


class Rate(NamedTuple):
    """
    Provides pair and value to an exchange rate
    """
    value: float
    pair: Pair

    def __mul__(self, other: Rate):
        common_ccy = set([self.pair.base, self.pair.quote]).intersection(
            set([other.pair.base, other.pair.quote]))
        assert common_ccy, "Pairs don't match"

        self_aux = self
        if self.pair.quote == other.pair.quote:
            other = Rate(1/other.value, other.pair.inverse)
        elif self.pair.base == other.pair.quote:
            self_aux = Rate(1/self.value, self.pair.inverse)
            other = Rate(1/other.value, other.pair.inverse)
        elif self.pair.base == other.pair.base:
            self_aux = Rate(1/self.value, self.pair.inverse)

        return Rate(self_aux.value * other.value, Pair(self_aux.pair.base, other.pair.quote))


class Pair(NamedTuple):
    """
    Base Class for Exchange Pairs
    """
    base: Currency
    quote: Currency

    # pylint: disable = missing-function-docstring;
    def __str__(self):
        return f"{self.base.value}_{self.quote.value}"
    # pylint: disable = unsubscriptable-object;

    @property
    def inverse(self) -> Pair:
        return Pair(self.quote, self.base)

    def get_rate(self, state: StateVariables) -> float:
        if self in state['market_price']:
            rate = Rate(state['market_price'].get(self), self)
        elif self.inverse in state['market_price']:
            rate = Rate(1 / state['market_price'].get(self.inverse), self)

        else:
            pairs = self.get_pairs(state)
            rate = pairs[0].get_rate(state)
            for pair in pairs[1:]:
                rate *= pair.get_rate(state)
        return rate

    def get_pairs(self, state) -> Union[Currency, Pair]:
        if isinstance(self.base, Fiat) and isinstance(self.quote, Fiat):
            pairs = [Pair(CryptoAsset.CELO, self.base),
                     Pair(CryptoAsset.CELO, self.quote)]
        elif isinstance(self.base, CryptoAsset) and isinstance(self.quote, CryptoAsset):
            pairs = [Pair(self.base, Fiat.USD), Pair(self.quote, Fiat.USD)]
        elif isinstance(self.base, Stable) and isinstance(self.quote, Stable):
            end_pair = self.get_atom_pair(state, match_base=False)
            return [Pair(self.base, end_pair.quote), end_pair]
        elif isinstance(self.base, CryptoAsset) and isinstance(self.quote, Fiat):
            pairs = Pair(self.base, CryptoAsset.CELO).get_pairs(
                state)
            pairs.extend([Pair(CryptoAsset.CELO, self.quote)])
        elif isinstance(self.base, CryptoAsset) and isinstance(self.quote, Stable):
            end_pair = self.get_atom_pair(state, match_base=False)
            pairs = [Pair(self.base, end_pair.quote), end_pair]
        elif isinstance(self.base, Stable) and isinstance(self.quote, Fiat):
            start_pair = self.get_atom_pair(state)
            pairs = [start_pair]
            pairs.extend(
                Pair(start_pair.quote, self.quote).get_pairs(state))
        else:
            pairs = self.inverse.get_pairs(state)
        return pairs

    def get_atom_pair(self, state, match_base=True):
        def match_reference(x):
            return self.base if x else self.quote
        market_prices = state['market_price']
        pair = [pair for pair in market_prices if pair.base ==
                match_reference(match_base)]
        assert len(
            pair) == 1, f'No or multiple pairs simulated for {match_reference(match_base)}'
        return pair[0]
