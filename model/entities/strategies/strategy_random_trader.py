"""
Strategy: Random Trader
"""
from cvxpy import Variable
import numpy as np

from experiments import simulation_configuration
from model.entities.trader import Trader
from model.utils.rng_provider import rngp

from .trader_strategy import TraderStrategy


# pylint: disable=using-constant-test
class RandomTrading(TraderStrategy):
    """
    Random Trading
    """

    def __init__(self, parent: Trader, acting_frequency=1):
        # The following is used to define the strategy and needs to be provided in subclass
        super().__init__(parent, acting_frequency)
        self.generate_sell_amounts()
        self.sell_amount = None
        self.rng = rngp.get_rng("RandomTrader", self.parent.account_id)

    def sell_reserve_asset(self, _params, prev_state):
        return self.orders[prev_state["timestep"]]["sell_reserve_asset"]

    def define_variables(self):
        self.variables["sell_amount"] = Variable(pos=True)

    def define_expressions(self, params, prev_state):
        """
        Defines and returns the expressions (made of variables and parameters)
        that are used in the optimization
        """

    def define_objective_function(self, _params, _prev_state):
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
        max_budget_stable = self.parent.balance.get(self.stable)
        max_budget_reserve_asset = self.parent.balance.get(self.reserve_asset)
        if self.sell_reserve_asset(params, prev_state):
            self.constraints.append(
                self.variables["sell_amount"]
                <= min(
                    max_budget_reserve_asset,
                    self.orders[prev_state["timestep"]]["sell_amount"]
                )
            )
        else:
            self.constraints.append(
                self.variables["sell_amount"]
                <= min(
                    max_budget_stable,
                    self.orders[prev_state["timestep"]]["sell_amount"]
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
        sell_gold = self.rng.binomial(1, 0.5, sample_size)
        orders = np.vstack(
            [sell_gold, np.abs(self.rng.normal(100, 5, size=sample_size))]
        )
        self.orders = np.core.records.fromarrays(
            orders, names=["sell_reserve_asset", "sell_amount"]
        )

    def calculate(self, _params, prev_state):
        """
        Calculates optimal trade if analytical solution is available
        """
        self.sell_amount = self.orders[prev_state["timestep"]]["sell_amount"]
