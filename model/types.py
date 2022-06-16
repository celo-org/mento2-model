"""
Various Python types used in the model
"""
from __future__ import annotations
from ast import List
from typing import Any, NamedTuple, Set, TypedDict, Union
from enum import Enum

from model.entities.balance import Balance


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

    def crypto_to_stable(self, prev_state):
        pair_2 = self.get_atom_pair(prev_state, match_base=False)
        if self.base is not CryptoAsset.CELO:
            pair_1 = Pair(self.base, pair_2.quote)
            rate_1 = pair_1.get_rate(prev_state)
            rate = pair_1.implicit_rate(pair_2, prev_state, self_rate=rate_1)
        else:
            pair_1 = Pair(
                self.base, pair_2.quote)
            pair_2 = Pair(self.quote, pair_2.quote)
            rate = pair_1.implicit_rate(pair_2, prev_state)
        return rate

    def crypto_to_fiat(self, prev_state):
        pair_1 = Pair(self.base, CryptoAsset.CELO)
        rate_1 = pair_1.get_rate(prev_state)
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
        pair_1 = self.get_atom_pair(prev_state)
        pair_2 = Pair(pair_1.quote, self.quote)
        rate_2 = pair_2.get_rate(prev_state)
        rate = pair_1.implicit_rate(pair_2, prev_state,  other_rate=rate_2)
        return rate

    def stable_to_stable(self, prev_state):
        pair_2 = self.get_atom_pair(prev_state, match_base=False)
        pair_1 = Pair(self.base, pair_2.quote)
        rate_1 = pair_1.get_rate(prev_state)
        rate = pair_1.implicit_rate(pair_2, prev_state, self_rate=rate_1)
        return rate

    def get_atom_pair(self, prev_state, match_base=True):
        def match_reference(x):
            return self.base if x else self.quote
        market_prices = prev_state['market_price']
        pair = [pair for pair in market_prices if pair.base ==
                match_reference(match_base)]
        assert len(
            pair) == 1, f'No or multiple pairs simulated for {match_reference(match_base)}'
        return pair[0]

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


class TraderConfig(NamedTuple):
    trader_type: TraderType
    count: int
    balance: Balance
    exchange: MentoExchange


class MentoExchangeConfig(NamedTuple):
    reserve_asset: CryptoAsset
    stable: Stable
    reference_fiat: Fiat
    reserve_fraction: float
    spread: float
    bucket_update_frequency_second: int
    max_sell_fraction_of_float: float


class MarketPriceConfig(NamedTuple):
    pair: Pair
    process: Any
    param_1: float
    param_2: float


class OracleConfig(NamedTuple):
    type: OracleType
    count: int
    aggregation: AggregationMethod
    delay: int
    reporting_interval: int
    price_threshold: int
    pairs: Set[Pair]


class ImpactDelayConfig(NamedTuple):
    model: ImpactDelayType
    param_1: float
