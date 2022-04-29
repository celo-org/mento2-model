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
    def sell_gold(self, params, prev_state):
        # Arb trade will sell CELO if  CELO/USD > CELO/cUSD
        return (
            prev_state["market_price"]["celo_usd"]
            < (1 - params["spread"])
            * prev_state["mento_buckets"]["cusd"]
            / prev_state["mento_buckets"]["celo"]
        )

    def define_variables(self):
        self.variables["sell_amount"] = Variable(pos=True)

    def define_expressions(self, params, prev_state):
        """
        Can be used as part of the objective and/or as constraints
        """
        if self.sell_gold(params, prev_state):
            nominator = (
                prev_state["mento_buckets"]["celo"]
                * prev_state["mento_buckets"]["cusd"]
            )
            denominator = (
                prev_state["mento_buckets"]["celo"] + self.variables["sell_amount"]
            ) * (
                prev_state["mento_buckets"]["celo"]
                - self.variables["sell_amount"] * (params["spread"] - 1)
            )
        else:
            nominator = (
                prev_state["mento_buckets"]["cusd"] + self.variables["sell_amount"]
            ) * (
                prev_state["mento_buckets"]["cusd"]
                - self.variables["sell_amount"] * (params["spread"] - 1)
            )
            denominator = (
                prev_state["mento_buckets"]["celo"]
                * prev_state["mento_buckets"]["cusd"]
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
        max_budget_cusd = 10000
        max_budget_celo = 10000
        if self.sell_gold(params, prev_state):
            self.constraints.append(self.variables["sell_amount"] <= max_budget_celo)
        else:
            self.constraints.append(self.variables["sell_amount"] <= max_budget_cusd)
