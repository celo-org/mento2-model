"""
Strategy: Arbitrage Trader
"""
from enum import Enum
import numpy as np

from model.types import MentoBuckets
from .trader_strategy import TraderStrategy

class TradingRegime(Enum):
    SELL_STABLE = "SELL_STABLE"
    SELL_RESERVE_ASSET = "SELL_RESERVE_ASSET"
    PASS = "PASS"


# pylint: disable=using-constant-test
# pylint: disable=duplicate-code
class ArbitrageTrading(TraderStrategy):
    """
    Arbitrage Trading
    """

    def __init__(self, parent, acting_frequency=1):
        # The following is used to define the strategy and needs to be provided in subclass
        super().__init__(parent, acting_frequency)
        self.sell_amount = None

    def sell_reserve_asset(self, _params, prev_state):
        # Arb trade will sell CELO if  CELO/USD > CELO/cUSD
        return self.trading_regime(prev_state) == TradingRegime.SELL_RESERVE_ASSET

    def trading_regime(self, prev_state) -> TradingRegime:
        """
        Indicates how the trader will act depending on the relation of mento price
        and market price
        """
        mento_buckets = self.mento_buckets(prev_state)
        mento_price = mento_buckets['stable'] / mento_buckets['reserve_asset']
        market_price = self.market_price(prev_state)

        price_up_profit = (
            market_price * (1 - self.exchange_config.spread)
            > mento_price
        )
        price_down_profit = (
            market_price / (1 - self.exchange_config.spread)
            < mento_price
        )

        if price_up_profit:
            return TradingRegime.SELL_STABLE
        if price_down_profit:
            return TradingRegime.SELL_RESERVE_ASSET
        return TradingRegime.PASS

    def define_expressions(self, _params, prev_state):
        """
        Defines and returns the expressions (made of variables and parameters)
        that are used in the optimization (random trader)
        """
        market_price = self.market_price(prev_state)
        mento_buckets = self.mento_buckets(prev_state)
        spread = self.exchange_config.spread

        if self.trading_regime(prev_state) == TradingRegime.SELL_STABLE:
            self.expressions["profit"] = (
                -1 * self.variables["sell_amount"]
                * mento_buckets['reserve_asset']
                * (1 - spread)
                / mento_buckets['stable']
                + (1 - spread) * self.variables["sell_amount"]
                + market_price * self.variables["sell_amount"]
            )
        elif self.trading_regime(prev_state) == TradingRegime.SELL_RESERVE_ASSET:
            self.expressions["profit"] = (
                -self.variables["sell_amount"]
                * mento_buckets['stable']
                * (1 - spread)
                / mento_buckets['reserve_asset']
                + (1 - spread) * self.variables["sell_amount"]
                + 1 / market_price * self.variables["sell_amount"]
            )

    def trader_passes_step(self, _params, prev_state):
        return (self.trading_regime(prev_state) == "PASS") or \
               (prev_state["timestep"] % self.acting_frequency != 0)

    # # pylint: disable=attribute-defined-outside-init
    def calculate(self, _params, prev_state):
        """
        Calculates optimal trade if analytical solution is available
        """
        market_price = self.market_price(prev_state)
        mento_buckets = self.mento_buckets(prev_state)
        spread = self.exchange_config.spread
        mento_price = mento_buckets['stable'] / mento_buckets['reserve_asset']

        if market_price * (1 - spread) > mento_price:
            self.sell_order_stable(
                mento_buckets,
                market_price,
                spread
            )
        elif market_price / (1 - spread) < mento_price:
            self.sell_order_reserve_asset(
                mento_buckets,
                market_price,
                spread
            )
        else:
            self.order = {"sell_amount": None}
        self.sell_amount = self.order["sell_amount"]

    def sell_order_stable(self, buckets: MentoBuckets, market_price: float, spread: float):
        """
        Calculate order for selling the stable
        """
        balance_stable = self.parent.balance.get(self.stable)
        balance_reserve_asset = self.parent.balance.get(self.reserve_asset)

        max_budget_stable = balance_stable + market_price * balance_reserve_asset
        sell_amount = self.optimal_sell_amount(
            buckets['stable'],
            buckets['reserve_asset'],
            market_price,
            spread
        )

        self.order = {
            "sell_amount": min(
                sell_amount,
                max_budget_stable,
            ),
            "sell_reserve_asset": False,
        }

    def sell_order_reserve_asset(
        self,
        buckets: MentoBuckets,
        market_price: float,
        spread: float):
        """
        Calculate order for selling the reserve currency
        """
        balance_stable = self.parent.balance.get(self.stable)
        balance_reserve_asset = self.parent.balance.get(self.reserve_asset)

        max_budget_celo = balance_reserve_asset + balance_stable / market_price
        sell_amount = self.optimal_sell_amount(
            buckets['reserve_asset'],
            buckets['stable'],
            1 / market_price,
            spread
        )

        self.order = {
            "sell_amount": min(
                sell_amount,
                max_budget_celo,
            ),
            "sell_reserve_asset": True,
        }

    # pylint: disable=no-self-use
    def optimal_sell_amount(self, bucket_sell, bucket_buy, price_buy_sell, spread):
        """
        bucket_sell: bucket of asset that is sold
        bucket_buy: bucket of asset that is bought
        price_buy_sell: buy asset / sell asset
        """
        sell_amount = (
            np.sqrt((1 - spread) * price_buy_sell * bucket_sell * bucket_buy)
            - bucket_sell
        ) / (1 - spread)
        return sell_amount
