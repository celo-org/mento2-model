"""
Strategy: Random Trader
"""
import numpy as np

from experiments import simulation_configuration

from model.parts.strategies import TraderStrategyAbstract


# pylint: disable=using-constant-test
class RandomTrading(TraderStrategyAbstract):
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

    def define_expressions(self, params, prev_state):
        """
        Defines and returns the expressions (made of variables and parameters)
        that are used in the optimization
        """

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
        # Todo add balance constraint to analytic method
        self.sell_amount = self.orders[prev_state["timestep"]]["sell_amount"]
