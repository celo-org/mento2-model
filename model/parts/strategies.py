"""
# Defines Strategies. Strategies:
 *have a convex objective_function (cvxpy objective function type)
 *have a set of convex constraints (cvxpy constraints type)
 *trigger optimal actions defined by the above (objective_function, constraints) via
 some Manager (buy_and_sell_manager, irp_manager, ...)
"""
import cvxpy
from cvxpy import Maximize, Minimize, Problem, Variable
from model.utils import update_from_signal


class StrategyAbstract:
    def __init__(self, acting_frequency):
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

    def solve(self):
        """
        Defines the solver to use and the respective parameters and runs the optimization
        """
        raise NotImplementedError('Subclasses must implement solve()')

    def optimize(self, params, prev_state):
        """
        Runs the optimization
        """
        self.define_variables()
        self.define_expressions(params, prev_state)
        self.define_objective_function(params, prev_state)
        self.define_constraints(params, prev_state)
        self.solve()

    def execute_optimal_action(self, params, prev_state):
        """
          Executes the optimal action depending on the optimization outcome
          """
        raise NotImplementedError('Subclasses must implement execute_optimal_action()')


class SellMax(StrategyAbstract):

    def __init__(
            self, acting_frequency, buy_and_sell_manager
    ):
        super().__init__(acting_frequency)
        self.buy_and_sell_manager = buy_and_sell_manager
        self.state_update_block = {
            "description": """
                Proof of concept: An actor using this strategy sells as much as he can
            """,
            'policies': {
                'actor_acts': None
            },
            'variables': {
                'celo_usd_price': update_from_signal('celo_usd_price')
            }
        }

    @staticmethod
    def sell_gold(params, prev_state):
        # Arb trade will sell CELO if  CELO/USD > CELO/cUSD
        return prev_state['celo_usd_price'] < prev_state['mento_rate']

    def define_variables(self):
        self.variables['sell_amount'] = Variable(pos=True)

    def define_expressions(self, params, prev_state):
        """
        Can be used as part of the objective and/or as constraints
        """
        if self.sell_gold(params, prev_state):
            nominator = prev_state['mento_buckets']['celo'] * prev_state['mento_buckets']['cusd']
            denominator = (
                (prev_state['mento_buckets']['celo'] + self.variables['sell_amount']) *
                (prev_state['mento_buckets']['celo'] - self.variables['sell_amount'] * (params['spread'] - 1))
            )
        else:
            nominator = (
                    (prev_state['mento_buckets']['cusd'] + self.variables['sell_amount']) *
                    (prev_state['mento_buckets']['cusd'] - self.variables['sell_amount'] * (params['spread'] - 1))
            )
            denominator = prev_state['mento_buckets']['celo'] * prev_state['mento_buckets']['cusd']

        mento_rate_after_trade = nominator / denominator

        self.expressions['mento_rate_after_trade'] = mento_rate_after_trade

    def define_objective_function(self, params, prev_state):
        """
        Defines a strategy by defining a convex objective_function, an optimization_direction
        and a set of convex constraints. A strategy can be use by an account to derive an optimal action.
        """
        self.objective_function = self.variables['sell_amount']
        self.optimization_direction = 'maximize'

    def define_constraints(self, params, prev_state):
        self.constraints = []
        # TODO: Get budget based on account
        max_budget_cusd = 10000
        max_budget_celo = 10000
        if self.sell_gold(params, prev_state):
            self.constraints.append(
                self.variables['sell_amount'] <= max_budget_celo
            )
        else:
            self.constraints.append(
                self.variables['sell_amount'] <= max_budget_cusd
            )

    def execute_optimal_action(self, params, prev_state):
        """
        Triggers optimal action and returns dict of state_variables after that action
        """

        if prev_state['timestep'] % self.acting_frequency != 0:
            # Actor not acting this timestep
            return self.buy_and_sell_manager.leave_all_state_variables_unchanged(
                prev_state=prev_state,
                policy_type='exchange'
            )

        self.optimize(params, prev_state)
        buy_amount = self.buy_and_sell_manager.calculate_buy_amount_constant_product_amm(
            params=params,
            prev_state=prev_state,
            sell_amount=self.variables['sell_amount'].value,
            sell_gold=self.sell_gold(params, prev_state)
        )
        optimal_trade = self.buy_and_sell_manager.create_trade(
            sell_gold=self.sell_gold(params, prev_state),
            sell_amount=self.variables['sell_amount'].value,
            buy_amount=buy_amount
        )
        state_variables_state_after_trade = self.buy_and_sell_manager.state_variables_state_after_trade(
            prev_state=prev_state,
            trade=optimal_trade
        )
        return state_variables_state_after_trade

    def solve(self):
        """
        If closed form solution is available, it goes here. Otherwise use CVXPY.
        """

        # Generate cvxpy optimization problem
        assert self.optimization_direction == 'minimize' or self.optimization_direction == 'maximize', \
            'Optimization direction not specified.'
        if self.optimization_direction == 'minimize':
            obj = Minimize(self.objective_function)
        else:
            obj = Maximize(self.objective_function)
        prob = Problem(obj, self.constraints)

        # The optimization problem of SellMax is quasi-convex
        try:
            prob.solve(solver=cvxpy.ECOS, abstol=1e-6, reltol=1e-6, max_iters=10000, verbose=False)
        except Exception as e:
            print(e)

        assert prob.status == 'optimal', 'Optimization NOT successful!'
        # print(f'Objective value in optimum is {prob.value}.')
        # print(self.variables['sell_amount'].value)
        # print(self.expressions['mento_rate_after_trade'].value)
