"""
Strategy: Random Trader
"""
import cvxpy
from cvxpy import Maximize, Minimize, Problem, Variable
import numpy as np

from experiments import simulation_configuration

from model.parts import buy_and_sell
from model.parts.strategies import StrategyAbstract


# pylint: disable=using-constant-test
class RandomTrading(StrategyAbstract):
    """
    Random Trading
    """

    def __init__(self, parent, acting_frequency=1):
        # The following is used to define the strategy and needs to be provided in subclass
        super().__init__(parent, acting_frequency)
        self.generate_sell_amounts()
        self.sell_amount = None

    def sell_gold(self, prev_state):
        # Arb trade will sell CELO if  CELO/USD > CELO/cUSD
        return self.orders[prev_state["timestep"]]["sell_gold"]

    def define_variables(self):
        self.variables["sell_amount"] = Variable(pos=True)

    def define_expressions(self, params, prev_state):
        """
        Defines and returns the expressions (made of variables and parameters)
        that are used in the optimization
        """

    def define_objective_function(self, params, prev_state):
        """
        Defines and returns the cvxpy objective_function
        """
        self.objective_function = self.variables["sell_amount"]
        self.optimization_direction = "maximize"

    def define_constraints(self, params, prev_state):
        """
        Defines and returns the constraints under which the optimization is conducted
        """
        self.constraints = []
        # TODO: Get budget based on account
        max_budget_cusd = self.parent.balance["cusd"]
        max_budget_celo = self.parent.balance["celo"]
        if self.sell_gold(prev_state):
            self.constraints.append(
                self.variables["sell_amount"]
                <= min(
                    max_budget_celo, self.orders[prev_state["timestep"]]["sell_amount"]
                )
            )
        else:
            self.constraints.append(
                self.variables["sell_amount"]
                <= min(
                    max_budget_cusd, self.orders[prev_state["timestep"]]["sell_amount"]
                )
            )

    def generate_sell_amounts(
        self,
        blocks_per_timestep=simulation_configuration.BLOCKS_PER_TIMESTEP,
        timesteps=simulation_configuration.TIMESTEPS,
    ):
        """
        This function generates lognormal returns
        """
        # timesteps_per_year = constants.blocks_per_year // blocks_per_timestep
        sample_size = timesteps * blocks_per_timestep + 1
        # TODO parametrise random params incl. seed
        sell_gold = np.random.binomial(1, 0.5, sample_size)
        orders = np.vstack(
            [sell_gold, np.abs(np.random.normal(100, 5, size=sample_size))]
        )
        self.orders = np.core.records.fromarrays(
            orders, names=["sell_gold", "sell_amount"]
        )

    def calculate(self, _params, prev_state):
        """
        Calculates optimal trade if analytical solution is available
        """
        self.sell_amount = self.orders[prev_state["timestep"]]["sell_amount"]

    # pylint: disable=broad-except
    def solve(self, params, prev_state):

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

    def optimize(self, params, prev_state):
        """
        Runs the optimization
        """

        if self.calculate:
            self.calculate(params, prev_state)
        else:
            self.define_variables()
            self.define_expressions(params, prev_state)
            self.define_objective_function(params, prev_state)
            self.define_constraints(params, prev_state)
            self.solve(params, prev_state)

    def return_optimal_trade(self, params, prev_state):
        """
        Returns the optimal action to be executed by actor
        """
        self.optimize(params=params, prev_state=prev_state)
        sell_amount = (
            self.variables["sell_amount"].value if self.variables else self.sell_amount
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
