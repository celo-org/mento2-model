"""
Strategy: Random Trader
"""
from cvxpy import Variable
import numpy as np

from experiments import simulation_configuration

from .trader_strategy import TraderStrategy


# pylint: disable=using-constant-test
class RandomTrading(TraderStrategy):
    """
    Random Trading
    """

    def __init__(self, parent, acting_frequency=1):
        # The following is used to define the strategy and needs to be provided in subclass
        super().__init__(parent, acting_frequency)
        self.generate_sell_amounts()
        self.sell_amount = None

    def sell_gold(self, _params, prev_state):
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
