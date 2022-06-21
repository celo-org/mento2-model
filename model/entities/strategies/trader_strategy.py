"""
# Defines Strategies. Strategies:
 *have a convex (or quasi-convex) objective_function (cvxpy objective function type)
 *have a set of convex constraints (cvxpy constraints type)
 *trigger optimal actions defined by the above (objective_function, constraints) via
 some Manager (buy_and_sell_manager, irp_manager, ...)
 *if closed-form solution is available, optimal action can be provided via closed form
  inside of solve() but the
 objective_function and the constraints should still be specified for completeness!
"""
from typing import TYPE_CHECKING
import logging
from cvxpy import Maximize, Minimize, Problem, Variable
import cvxpy

from model.types.base import MentoBuckets
from model.types.pair import Pair
from model.types.configs import MentoExchangeConfig
if TYPE_CHECKING:
    from model.entities.trader import Trader


class TraderStrategy:
    """
    Base trader strategy class to solve a convex optimisation problem.
    Subclasses are responsible for defining the strategy via constraints.

    """
    parent: "Trader"
    exchange_config: MentoExchangeConfig

    def __init__(self, parent: "Trader", acting_frequency):
        self.parent = parent
        self.acting_frequency = acting_frequency
        self.exchange_config = self.mento.configs.get(self.parent.config.exchange)

        # The following is used to define the strategy and needs to be
        #  provided in subclass
        self.variables = {}
        self.expressions = {}
        self.objective_function = None
        self.optimization_direction = None
        self.constraints = []
        # TODO order vs sell_amount ???
        self.sell_amount = None
        self.order = None

    @property
    def reference_fiat(self):
        return self.exchange_config.reference_fiat

    @property
    def stable(self):
        return self.exchange_config.stable

    @property
    def reserve_asset(self):
        return self.exchange_config.reserve_asset

    @property
    def mento(self):
        return self.parent.mento

    def sell_reserve_asset(self, _params, _prev_state):
        """
        Provides a function indicating the direction of the mento cashflow
        wether we sell or buy the reserve currency, which is CELO in
        the v1 AMM, but could be wBTC or ETH.
        """
        raise NotImplementedError("Subclasses must implement sell_reserve_asset()")

    def define_variables(self):
        self.variables["sell_amount"] = Variable(pos=True)

    def define_expressions(self, _params, _prev_state):
        """
        Defines and returns the expressions (made of variables and parameters)
        that are used in the optimization
        """
        raise NotImplementedError("Subclasses must implement define_expressions()")

    def define_constraints(self, params, prev_state):
        """
        Defines and returns the constraints under which the optimization is conducted
        """
        self.constraints = []
        # TODO: Get budget based on account
        max_budget_stable = self.parent.balance.get(self.stable)
        max_budget_reserve_asset = self.parent.balance.get(self.reserve_asset)
        if self.sell_reserve_asset(params, prev_state):
            self.constraints.append(
                self.variables["sell_amount"] <= max_budget_reserve_asset)
        else:
            self.constraints.append(self.variables["sell_amount"] <= max_budget_stable)

    def define_objective_function(self, _params, _prev_state):
        """
        Defines and returns the cvxpy objective_function
        """
        self.objective_function = self.variables["sell_amount"]
        self.optimization_direction = "maximize"

    def solve(self, _params, _prev_state):
        """
        Solves the optimisation problem algorithmically
        """
        # Generate cvxpy optimization problem
        assert self.optimization_direction in (
            "minimize",
            "maximize",
        ), "Optimization direction not specified."
        if self.optimization_direction == "minimize":
            obj = Minimize(self.objective_function)
        else:
            obj = Maximize(self.objective_function)
        prob = Problem(obj, self.constraints)

        # The optimization problem of SellMax is quasi-convex
        prob.solve(
            solver=cvxpy.ECOS,
            abstol=1e-6,
            reltol=1e-6,
            max_iters=10000,
            verbose=True,
        )

        assert prob.status == "optimal", "Optimization NOT successful!"
        logging.debug('Objective value in optimum is %s', prob.value)
        logging.debug(self.variables['sell_amount'].value)
        logging.debug(self.expressions['oracle_rate_after_trade'].value)

    # pylint: disable=duplicate-code
    def optimize(self, params, prev_state):
        """
        Runs the optimization
        """
        # TODO this is a bit dirty
        if hasattr(self, "calculate"):
            self.calculate(params, prev_state)
        else:
            self.define_variables()
            self.define_expressions(params, prev_state)
            self.define_objective_function(params, prev_state)
            self.define_constraints(params, prev_state)
            self.solve(params, prev_state)

    # pylint: disable=duplicate-code

    # pylint: disable=no-self-use
    def minimise_price_impact(self, sell_amount, sell_reserve_asset, params):
        """
        trader reduces sell amount to reduce market impact
        """
        # Todo logic is probably wrong, fix!
        if sell_reserve_asset:
            sell_amount_adjusted = min(
                params["average_daily_volume"].get(
                    Pair(self.stable, self.reference_fiat)),
                sell_amount
            )
        elif not sell_reserve_asset:
            sell_amount_adjusted = min(
                params["average_daily_volume"].get(
                    Pair(self.reserve_asset, self.reference_fiat)),
                sell_amount
            )
        return sell_amount_adjusted

    def trader_passes_step(self, _params, prev_state):
        return prev_state["timestep"] % self.acting_frequency != 0

    def return_optimal_trade(self, params, prev_state):
        """
        Returns the optimal action to be executed by actor
        """
        if self.trader_passes_step(params, prev_state):
            # Actor not acting this timestep
            trade = None
        else:
            self.optimize(params=params, prev_state=prev_state)
            sell_amount = (
                self.variables["sell_amount"].value
                if self.variables
                else self.sell_amount
            )
            if sell_amount is None or sell_amount == 0:
                trade = None
            else:
                sell_reserve_asset = self.sell_reserve_asset(params, prev_state)
                sell_amount = self.minimise_price_impact(
                    sell_amount, sell_reserve_asset, params)
                buy_amount = self.mento.get_buy_amount(
                    exchange=self.parent.config.exchange,
                    sell_amount=sell_amount,
                    sell_reserve_asset=sell_reserve_asset,
                    prev_state=prev_state,
                )

                trade = {
                    "sell_reserve_asset": sell_reserve_asset,
                    "sell_amount": sell_amount,
                    "buy_amount": buy_amount,
                }
        return trade

    def market_price(self, prev_state) -> float:
        # TODO: Do we need to quote in equivalent Fiat for Stable?
        return (
            prev_state["market_price"].get(
                Pair(self.reserve_asset, self.reference_fiat))
            / prev_state["market_price"].get(Pair(self.stable, self.reference_fiat))
        )

    def mento_buckets(self, prev_state) -> MentoBuckets:
        return prev_state["mento_buckets"].get(self.parent.config.exchange)
