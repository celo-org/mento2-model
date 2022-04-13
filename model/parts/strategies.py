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

# pylint: disable= missing-class-docstring
# pylint: disable=broad-except
class StrategyAbstract:
    def __init__(self, parent, acting_frequency):
        self.parent = parent
        self.acting_frequency = acting_frequency

        # The following is used to define the strategy and needs to be provided in subclass
        self.variables = {}
        self.expressions = {}
        self.objective_function = None
        self.optimization_direction = None
        self.constraints = []
        self.state_update_block = None

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

    def solve(self, params, prev_state):
        """
        Defines the solver to use and the respective parameters and runs the
        optimization
        """
        raise NotImplementedError("Subclasses must implement solve()")

    # def optimize(self, params, prev_state):
    #     """
    #     Runs the optimization
    #     """
    #     self.define_variables()
    #     self.define_expressions(params, prev_state)
    #     self.define_objective_function(params, prev_state)
    #     self.define_constraints(params, prev_state)
    #     self.solve(params, prev_state)

    # def execute_optimal_action(self, params, prev_state):
    #     """
    #       Executes the optimal action depending on the optimization outcome
    #       """
    #     raise NotImplementedError('Subclasses must implement
    #  execute_optimal_action()')
