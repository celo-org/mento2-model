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
from cvxpy import Maximize, Minimize, Problem, Variable
import cvxpy
from model.entities.balance import Balance
from model.parts import buy_and_sell

# pylint: disable= missing-class-docstring
# pylint: disable=broad-except
class TraderStrategy:
    def __init__(self, parent, acting_frequency):
        self.parent = parent
        self.acting_frequency = acting_frequency

        # The following is used to define the strategy and needs to be
        #  provided in subclass
        self.variables = {}
        self.expressions = {}
        self.objective_function = None
        self.optimization_direction = None
        self.constraints = []
        self.state_update_block = None
        # TODO order vs sell_amount ???
        self.sell_amount = None
        self.order = None

    def sell_gold(self, prev_state, params):
        """
        Provides a function indicating the direction of the celo cashflow
        """
        raise NotImplementedError("Subclasses must implement sell_gold()")

    def define_variables(self):
        self.variables["sell_amount"] = Variable(pos=True)

    def define_expressions(self, params, prev_state):
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
        max_budget_cusd = self.parent.balance["cusd"]
        max_budget_celo = self.parent.balance["celo"]
        if self.sell_gold(prev_state, params):
            self.constraints.append(self.variables["sell_amount"] <= max_budget_celo)

        else:
            self.constraints.append(self.variables["sell_amount"] <= max_budget_cusd)

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
        try:
            prob.solve(
                solver=cvxpy.ECOS,
                abstol=1e-6,
                reltol=1e-6,
                max_iters=10000,
                verbose=True,
            )

        except Exception as error:
            print(error)

        assert prob.status == "optimal", "Optimization NOT successful!"
        # print(f'Objective value in optimum is {prob.value}.')
        # print(self.variables['sell_amount'].value)
        # print(self.expressions['mento_rate_after_trade'].value)

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

    # def create_meta_order(self, trade, params):
    #     if trade['sell_gold'] == True:
    #         buy_amount = min(1/10 * params['average_daily_volume']['cusd_usd'],
    #  trade['buy_amount'])
    #     elif trade['sell_gold'] == False:
    #         buy_amount = min(1/10 * params['average_daily_volume']['celo_usd'],
    #  trade['buy_amount'])
    #     return

    # pylint: disable=no-self-use
    def minimise_price_impact(self, sell_amount, sell_gold, params):
        """
        trader reduces sell amount to reduce market impact
        """
        # Todo logic is probably wrong, fix!
        if sell_gold:

            sell_amount_adjusted = min(
                params["average_daily_volume"]["cusd_usd"], sell_amount
            )
        elif not sell_gold:
            sell_amount_adjusted = min(
                params["average_daily_volume"]["celo_usd"], sell_amount
            )
        return sell_amount_adjusted

    def trader_passes_step(self, prev_state, _params):
        return prev_state["timestep"] % self.acting_frequency != 0

    def return_optimal_trade(self, params, prev_state):
        """
        Returns the optimal action to be executed by actor
        """
        if self.trader_passes_step(prev_state, params):
            # Actor not acting this timestep
            trade = None
        else:
            self.optimize(params=params, prev_state=prev_state)
            sell_amount = (
                self.variables["sell_amount"].value
                if self.variables
                else self.sell_amount
            )
            if sell_amount is None:
                trade = None
            else:
                sell_gold = self.sell_gold(prev_state, params)
                sell_amount = self.minimise_price_impact(sell_amount, sell_gold, params)
                buy_amount = buy_and_sell.get_buy_amount(
                    params=params,
                    prev_state=prev_state,
                    sell_amount=sell_amount,
                    sell_gold=sell_gold,
                )

                trade = {
                    "sell_gold": sell_gold,
                    "sell_amount": sell_amount,
                    "buy_amount": buy_amount,
                }

        return trade

    @staticmethod
    def portfolio_balancing(account, sell_amount, sell_gold, prev_state):
        """
        trader strategy to balance portfolio for maximum arbitrage profit
        """
        if sell_gold and account.balance["celo"] < sell_amount:
            price_celo_cusd = (
                prev_state["market_price"]["celo_usd"]
                / prev_state["market_price"]["cusd_usd"]
            )
            # delta_celo = sell_amount - self.balance["celo"]
            delta_cusd = -account.balance["cusd"]
            delta_celo = -delta_cusd / price_celo_cusd
            account.balance += Balance(cusd=delta_cusd, celo=delta_celo)
        elif (not sell_gold) and (account.balance["cusd"] < sell_amount):
            price_celo_cusd = (
                prev_state["market_price"]["celo_usd"]
                / prev_state["market_price"]["cusd_usd"]
            )
            delta_celo = -account.balance["celo"]
            delta_cusd = -delta_celo * price_celo_cusd
            account.balance += Balance(cusd=delta_cusd, celo=delta_celo)
