"""
# Defines Strategies. Strategies:
 *have a convex objective_function (cvxpy objective function type)
 *have a set of convex constraints (cvxpy constraints type)
 *trigger optimal actions defined by the above (objective_function, constraints) via
 some Manager (buy_and_sell_manager, irp_manager, ...)
"""
import cvxpy
from cvxpy import (Maximize, Minimize, Problem, Variable, Parameter)
from buy_and_sell import buy_and_sell_manager
from utils.cvxpy_helpers import turn_dict_to_cvxpy_params_dict


class StrategyAbstract:
    def __init__(self, description, policy_name):
        # The following is used to create the related state-update-block
        self.description = description
        self.policy_name = policy_name
        # The following is used to define the strategy
        self.variables = {}
        self.expressions = {}
        self.objective_function = None
        self.optimization_direction = None
        self.constraints = []

    def define_variables(self):
        """
        Defines and returns the variables wrt. which the optimization is conducted
        """
        raise NotImplementedError('Subclasses must implement define_variables()')

    def define_expressions(self, params, prev_state):
        """
        Defines and returns the expressions (made of variables and parameters) that are used in the optimization
        """
        raise NotImplementedError('Subclasses must implement define_expressions()')

    def define_objective_function(self, params, prev_state):
        """
        Defines and returns the cvxpy objective_function
        """
        raise NotImplementedError('Subclasses must implement define_objective_function()')

    def define_constraints(self, params, prev_state):
        """
        Defines and returns the constraints under which the optimization is conducted
        """
        raise NotImplementedError('Subclasses must implement define_constraints()')

    def optimize(self, params, prev_state):
        """
        Runs the optimization
        """
        self.define_variables()
        self.define_expressions(params, prev_state)
        self.define_objective_function(params, prev_state)
        self.define_constraints(params, prev_state)

        # Generate cvxpy optimization problem
        assert (
            self.optimization_direction == 'minimize' or self.optimization_direction == 'maximize',
            'It was not specified in subclass whether optimization is minimization or maximization.'
        )
        if self.optimization_direction == 'minimize':
            obj = Minimize(self.objective_function)
        else:
            obj = Maximize(self.objective_function)
        prob = Problem(obj, self.constraints)

        # Solve the optimization problem
        try:
            prob.solve(solver=cvxpy.ECOS, abstol=1e-6, reltol=1e-6, max_iters=10000, verbose=False)

        except Exception as e:
            print(e)

        assert(prob.status == 'optimal', 'Optimization NOT successful!')
        print(f'Objective value in optimum is {prob.value}.')

    def execute_optimal_action(self, params, prev_state):
        """
          Executes the optimal action depending on the optimization outcome
          """
        raise NotImplementedError('Subclasses must implement execute_optimal_action()')


class BuyAndSellArb(StrategyAbstract):

    def __init__(
            self
    ):
        super().__init__(
            description='Actor arb trades with buy-and-sell feature of mento until celo/cusd equals celo/usd',
            policy_name='arb_trader'
        )

    @staticmethod
    def sell_gold(params, prev_state):
        # Arb trade will sell CELO if  CELO/USD > CELO/cUSD
        return params['celo_usd_price'] > prev_state['mento_rate']

    def define_variables(self):
        self.variables['sell_amount'] = Variable(nonneg=False)

    def define_expressions(self, params, prev_state):

        # If cvxpy objects are passed to functions instead of numbers, a cvxpy expr is returned instead of a number
        cvxpy_params = turn_dict_to_cvxpy_params_dict(params)
        cvxpy_prev_state = turn_dict_to_cvxpy_params_dict(prev_state)
        buy_amount = buy_and_sell_manager.calculate_buy_amount_constant_product_amm(
            params=cvxpy_params,
            prev_state=cvxpy_prev_state,
            sell_amount=self.variables['sell_amount'],
            sell_gold=self.sell_gold
        )
        if self.sell_gold:
            mento_rate_after_trade = (
                (prev_state['mento_buckets']['cusd'] - buy_amount) /
                (prev_state['mento_buckets']['celo'] + self.variables['sell_amount'])
            )

        else:
            mento_rate_after_trade = (
                (prev_state['mento_buckets']['cusd'] + self.variables['sell_amount']) /
                (prev_state['mento_buckets']['celo'] - buy_amount)
            )

        self.expressions['buy_amount'] = buy_amount
        self.expressions['mento_rate_after_trade'] = mento_rate_after_trade

    def define_objective_function(self, params, prev_state):
        """
        Defines a strategy by defining a convex objective_function, an optimization_direction
        and a set of convex constraints. A strategy can be use by an account to derive an optimal action.
        """

        # Define objective function and optimization_direction
        self.objective_function = cvxpy.abs(
            params['celo_usd_price'] - self.expressions['mento_rate_after_trade']
        )
        self.optimization_direction = 'minimize'

    def define_constraints(self, params, prev_state):
        self.constraints = []
        # TODO: Get budget based on account
        max_budget_cusd = 100000
        max_budget_celo = 100000
        sell_gold = params['celo_usd_price'] > prev_state['mento_rate']
        if sell_gold:
            self.constraints .append(
                self.expressions['sell_amount'] <= max_budget_celo
            )
        else:
            self.constraints .append(
                self.expressions['sell_amount'] <= max_budget_cusd
            )

    def execute_optimal_action(self, params, prev_state):
        """
        Triggers optimal action and returns dict of state_variables after that action
        """

        self.optimize(params, prev_state)

        optimal_trade = buy_and_sell_manager.create_trade(
            sell_gold=self.sell_gold(params, prev_state),
            sell_amount=self.variables['sell_amount'].value,
            buy_amount=self.expressions['buy_amount'].value
        )
        state_variables_state_after_trade = buy_and_sell_manager.state_variables_state_after_trade(
            prev_state=prev_state,
            trade=optimal_trade
        )
        return state_variables_state_after_trade
