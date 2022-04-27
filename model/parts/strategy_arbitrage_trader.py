"""
Strategy: Arbitrage Trader
"""
import numpy as np

from model.parts.strategies import TraderStrategyAbstract


# pylint: disable=using-constant-test
# pylint: disable=duplicate-code
class ArbitrageTrading(TraderStrategyAbstract):
    """
    Random Trading
    """

    def __init__(self, parent, acting_frequency=1):
        # The following is used to define the strategy and needs to be provided in subclass
        super().__init__(parent, acting_frequency)
        self.sell_amount = None

    def sell_gold(self, prev_state):
        # Arb trade will sell CELO if  CELO/USD > CELO/cUSD
        return self.order["sell_gold"]

    def define_expressions(self, params, prev_state):
        """
        Defines and returns the expressions (made of variables and parameters)
        that are used in the optimization (random trader)
        """

    # # pylint: disable=attribute-defined-outside-init
    def calculate(self, params, prev_state):
        """
        Calculates optimal trade if analytical solution is available
        """
        price_celo_cusd = (
            prev_state["market_price"]["celo_usd"]
            / prev_state["market_price"]["cusd_usd"]
        )
        if (price_celo_cusd) * (1 - params["spread"]) > prev_state["mento_buckets"][
            "cusd"
        ] / prev_state["mento_buckets"]["celo"]:
            self.sell_order_cusd(
                prev_state["mento_buckets"]["cusd"],
                prev_state["mento_buckets"]["celo"],
                price_celo_cusd,
                params["spread"],
            )
        elif (
            price_celo_cusd / (1 - params["spread"])
            < prev_state["mento_buckets"]["cusd"] / prev_state["mento_buckets"]["celo"]
        ):
            self.sell_order_celo(
                prev_state["mento_buckets"]["cusd"],
                prev_state["mento_buckets"]["celo"],
                price_celo_cusd,
                params["spread"],
            )
        else:
            self.order = {"sell_amount": None}
        self.sell_amount = self.order["sell_amount"]

    def sell_order_cusd(self, bucket_cusd, bucket_celo, price_celo_cusd, spread):
        balance_cusd = self.parent.balance["cusd"]
        balance_celo = self.parent.balance["celo"]
        max_budget_cusd = balance_cusd + price_celo_cusd * balance_celo
        sell_amount = self.optimal_sell_amount(
            bucket_cusd, bucket_celo, price_celo_cusd, spread
        )
        self.order = {
            "sell_amount": min(
                sell_amount,
                max_budget_cusd,
            ),
            "sell_gold": False,
        }

    def sell_order_celo(self, bucket_cusd, bucket_celo, price_celo_cusd, spread):
        balance_cusd = self.parent.balance["cusd"]
        balance_celo = self.parent.balance["celo"]
        max_budget_celo = balance_celo + balance_cusd / price_celo_cusd
        sell_amount = self.optimal_sell_amount(
            bucket_celo, bucket_cusd, 1 / price_celo_cusd, spread
        )

        self.order = {
            "sell_amount": min(
                sell_amount,
                max_budget_celo,
            ),
            "sell_gold": True,
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
