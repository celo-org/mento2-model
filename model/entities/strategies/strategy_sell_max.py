"""
Sell Max Strategy
"""
from cvxpy import Variable
from .trader_strategy import TraderStrategy

class SellMax(TraderStrategy):
    """
    Sell Max Amount
    """

    def __init__(self, parent, acting_frequency=1000):
        super().__init__(parent, acting_frequency)
        self.sell_amount = None

    # @staticmethod
    def sell_reserve_currency(self, _params, prev_state):
        # Arb trade will sell reserve_currency if market price > mento price
        mento_buckets = self.mento_buckets(prev_state)
        return (
            prev_state["market_price"].get(self.reserve_currency).get(self.stable_fiat)
            < (1 - self.exchange_config.spread)
            * mento_buckets.stable
            / mento_buckets.reserve_currency
        )

    def define_variables(self):
        self.variables["sell_amount"] = Variable(pos=True)

    def define_expressions(self, params, prev_state):
        """
        Can be used as part of the objective and/or as constraints
        """
        mento_buckets = self.mento_buckets(prev_state)
        spread = self.exchange_config.spread

        if self.sell_reserve_currency(params, prev_state):
            nominator = (
                mento_buckets.reserve_currency
                * mento_buckets.stable
            )
            denominator = (
                mento_buckets.reserve_currency + self.variables["sell_amount"]
            ) * (
                mento_buckets.reserve_currency - self.variables["sell_amount"] * (spread - 1)
            )
        else:
            nominator = (
                mento_buckets.stable + self.variables["sell_amount"]
            ) * (
                mento_buckets.stable
                - self.variables["sell_amount"] * (spread - 1)
            )
            denominator = (
                mento_buckets.reserve_currency * mento_buckets.stable
            )

        oracle_rate_after_trade = nominator / denominator

        self.expressions["oracle_rate_after_trade"] = oracle_rate_after_trade

    def define_objective_function(self, _params, _prev_state):
        """
        Defines a strategy by defining a convex objective_function, an
         optimization_direction
        and a set of convex constraints. A strategy can be use by an
         account to derive an optimal action.
        """
        self.objective_function = self.variables["sell_amount"]
        self.optimization_direction = "maximize"

    def define_constraints(self, params, prev_state):
        self.constraints = []
        # TODO: Get budget based on account
        max_budget_stable = 10000
        max_budget_reserve_currency = 10000
        if self.sell_reserve_currency(params, prev_state):
            self.constraints.append(self.variables["sell_amount"] <= max_budget_reserve_currency)
        else:
            self.constraints.append(self.variables["sell_amount"] <= max_budget_stable)
