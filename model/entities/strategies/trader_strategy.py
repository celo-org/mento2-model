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
from cvxpy import Maximize, Minimize, Problem
import cvxpy
from model.parts import buy_and_sell

# pylint: disable=broad-except
class TraderStrategy:
    """
    Base TraderStrategy class that abstracts solving
    convex optimization problems, the definition of
    which lives in subclasses.
    """
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
        self.sell_amount = None

    def sell_gold(self, prev_state):
        """
        Provides a function indicating the direction of the celo cashflow
        """
        raise NotImplementedError("Subclasses must implement sell_gold()")

    def define_variables(self):
        """
        Defines and returns the variables wrt. which the optimization is conducted
        """
        raise NotImplementedError("Subclasses must implement define_variables()")

    def define_expressions(self, params, prev_state):
        """
        Defines and returns the expressions (made of variables and parameters)
        that are used in the optimization
        """
        raise NotImplementedError("Subclasses must implement define_expressions()")

    def define_objective_function(self, params, prev_state):
        """
        Defines and returns the cvxpy objective_function
        """
        raise NotImplementedError(
            "Subclasses must implement define_objective_function()"
        )

    def define_constraints(self, params, prev_state):
        """
        Defines and returns the constraints under which the optimization is conducted
        """
        raise NotImplementedError("Subclasses must implement define_constraints()")

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
                verbose=False,
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
    def return_optimal_trade(self, params, prev_state):
        """
        Returns the optimal action to be executed by actor
        """
        if prev_state["timestep"] % self.acting_frequency != 0:
            # Actor not acting this timestep
            trade = None
        else:
            self.optimize(params=params, prev_state=prev_state)
            sell_amount = (
                self.variables["sell_amount"].value
                if self.variables
                else self.sell_amount
            )
            buy_amount = buy_and_sell.get_buy_amount(
                params=params,
                prev_state=prev_state,
                sell_amount=sell_amount,
                sell_gold=self.sell_gold(prev_state),
            )

            trade = {
                "sell_gold": self.sell_gold(prev_state),
                "sell_amount": sell_amount,
                "buy_amount": buy_amount,
            }

        return trade
