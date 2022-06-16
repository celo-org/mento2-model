"""
Various Python types used in the model
"""
from __future__ import annotations
from ast import List
from typing import NamedTuple, TypedDict, Union
from enum import Enum


class SerializableEnum(Enum):
    def __str__(self):
        return self.value


class TraderType(Enum):
    """
    different account holders
    """
    ARBITRAGE_TRADER = "ArbitrageTrading"
    RANDOM_TRADER = "RandomTrading"
    MAX_TRADER = "SellMax"


class Stable(SerializableEnum):
    """
    Celo Stable assets
    """
    CUSD = "cusd"
    CREAL = "creal"
    CEUR = "ceur"


class CryptoAsset(SerializableEnum):
    CELO = "celo"
    ETH = "eth"
    BTC = "btc"
    DAI = "dai"


class Fiat(SerializableEnum):
    USD = "usd"
    EUR = "eur"
    BRL = "brl"


class MentoExchange(SerializableEnum):
    CUSD_CELO = "cusd_celo"
    CREAL_CELO = "creal_celo"
    CEUR_CELO = "ceur_celo"


Currency = Union[Stable, Fiat, CryptoAsset]


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

    def get_rate(self, prev_state) -> float:
        market_prices = prev_state['market_price']

        if self in market_prices:
            rate = market_prices.get(self)

        elif isinstance(self.base, Fiat) and isinstance(self.quote, Fiat):
            rate = self.fiat_to_fiat(prev_state)

        elif isinstance(self.base, CryptoAsset) and isinstance(self.quote, CryptoAsset):

            rate = self.crypto_to_crypto(prev_state)

        elif isinstance(self.base, Stable) and isinstance(self.quote, Stable):

            rate = self.stable_to_stable(prev_state)

        elif isinstance(self.base, CryptoAsset) and isinstance(self.quote, Fiat):
            rate = self.crypto_to_fiat(prev_state)

        elif isinstance(self.base, CryptoAsset) and isinstance(self.quote, Stable):

            rate = self.crypto_to_stable(prev_state)

        elif isinstance(self.base, Stable) and isinstance(self.quote, Fiat):

            rate = self.stable_to_fiat(prev_state)

        else:
            pair_reversed = Pair(self.quote, self.base)
            rate = pair_reversed.get_rate(prev_state)**(-1)

        return rate

    def stable_to_stable(self, prev_state):
        market_prices = prev_state['market_price']
        pair_1 = [pair for pair in market_prices if pair.base == self.base]
        assert len(pair_1) == 1, f'No or multiple pairs simulated for {self.base}'
        pair_4 = [pair for pair in market_prices if pair.base == self.quote]
        assert len(pair_4) == 1, f'No or multiple pairs simulated for {self.quote}'
        pair_1 = pair_1[0]
        pair_4 = pair_4[0]
        pair_2 = Pair(CryptoAsset.CELO, pair_1.quote)
        pair_3 = Pair(CryptoAsset.CELO, pair_4.quote)
        pair_1_2, rate_1_2 = pair_1.implicit_rate(
            pair_2, prev_state, rate_only=False)
        pair_1_3, rate_1_3 = pair_1_2.implicit_rate(
            pair_3, prev_state, self_rate=rate_1_2, rate_only=False)
        rate = pair_1_3.implicit_rate(pair_4, prev_state, self_rate=rate_1_3)
        return rate

    def crypto_to_stable(self, prev_state):
        market_prices = prev_state['market_price']
        pair_2 = [pair for pair in market_prices if pair.base == self.quote]
        assert len(pair_2) == 1, f'No or multiple pairs simulated for {self.base}'
        pair_2 = pair_2[0]
        if self.base is not CryptoAsset.CELO:
            pair_1 = Pair(self.base, pair_2.quote)
            rate_1 = pair_1.crypto_to_fiat(prev_state)

            rate = pair_1.implicit_rate(pair_2, prev_state, self_rate=rate_1)
        else:
            pair_1 = Pair(
                self.base, pair_2.quote)

            pair_2 = Pair(self.quote, pair_1.quote)

            rate = pair_1.implicit_rate(pair_2, prev_state)
        return rate

    def crypto_to_fiat(self, prev_state):
        pair_1 = Pair(self.base, CryptoAsset.CELO)
        rate_1 = pair_1.crypto_to_crypto(prev_state)
        pair_2 = Pair(CryptoAsset.CELO, self.quote)

        rate = pair_1.implicit_rate(
            pair_2, prev_state, self_rate=rate_1)
        return rate

    def crypto_to_crypto(self, prev_state):
        pair_1 = Pair(self.base, Fiat.USD)
        pair_2 = Pair(self.quote, Fiat.USD)
        rate = pair_1.implicit_rate(
            pair_2, prev_state)
        return rate

    def fiat_to_fiat(self, prev_state):
        pair_1 = Pair(CryptoAsset.CELO, self.base)
        pair_2 = Pair(CryptoAsset.CELO, self.quote)
        rate = pair_1.implicit_rate(
            pair_2, prev_state)

        return rate

    def stable_to_fiat(self, prev_state):
        market_prices = prev_state['market_price']
        pair_1 = [pair for pair in market_prices if pair.base == self.base]
        assert len(pair_1) == 1, f'No or multiple pairs simulated for {self.base}'
        pair_1 = pair_1[0]
        pair_2 = Pair(pair_1.quote, self.quote)
        rate_2 = pair_2.fiat_to_fiat(prev_state)
        rate = pair_1.implicit_rate(pair_2, prev_state,  other_rate=rate_2)
        return rate

    def implicit_rate(self, other: Pair, prev_state, self_rate=None, other_rate=None,
                      rate_only: bool = True) -> Union(float, List[Pair, float]):
        """
        Provides the implicit rate of two pairs if self and other have
        a currency in common. self provides the base of the implicit pair
        """
        market_prices = prev_state['market_price']
        rate_1 = market_prices.get(
            self) if self_rate is None else self_rate
        rate_2 = market_prices.get(other) if other_rate is None else other_rate
        if self.quote == other.base:
            base = self.base
            quote = other.quote
            rate = rate_1 * rate_2
        elif self.quote == other.quote:
            base = self.base
            quote = other.base
            rate = rate_1 * rate_2**(-1)
        elif self.base == other.quote:
            base = self.quote
            quote = other.base
            rate = rate_1**(-1) * rate_2**(-1)
        elif self.base == other.base:
            base = self.quote
            quote = other.quote
            rate = rate_1**(-1) * rate_2
        if rate_only:
            output = rate
        elif not rate_only:
            output = [Pair(base, quote), rate]
        return output


class MentoBuckets(TypedDict):
    stable: float
    reserve_asset: float


class MarketPriceModel(Enum):
    QUANTLIB = "quantlib"
    PRICE_IMPACT = "price_impact"
    HIST_SIM = "hist_sim"
    SCENARIO = "scenario"


class PriceImpact(Enum):
    ROOT_QUANTITY = "root_quantity"
    CUSTOM = "custom"


class ImpactDelayType(Enum):
    INSTANT = "instant"
    NBLOCKS = "nblocks"


class AggregationMethod(Enum):
    IDENTITY = 'indentity'


class OracleType(Enum):
    SINGLE_SOURCE = 'single_source'
