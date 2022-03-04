"""
Provides Traders / Actors
"""

import numpy as np
from experiments import simulation_configuration
from model.generators.buy_and_sell import BuyAndSellGenerator


class AccountHolder:
    """
    Agent / Account Holder
    """

    def __init__(
        self, parent, account_id, account_name, balance, account_type=None, orders=None
    ):
        self.parent = parent
        self.account_id = account_id
        self.account_name = account_name
        self.balance = {"celo": balance["celo"], "cusd": balance["celo"]}
        self.account_type = account_type
        self.dummy = 0
        self.orders = orders
        self.generate_sell_amounts()

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

    def current_orders(self, state):
        return self.orders[:, state]

    def execute(
        self,
        buy_sell_generator: BuyAndSellGenerator,
        substep,
        state_history,
        prev_state,
    ):
        """
        Making pylint happy
        """
        sell_amount = self.orders["sell_amount"][prev_state["timestep"]]
        sell_gold = self.orders["sell_gold"][prev_state["timestep"]]
        states, deltas = buy_sell_generator.exchange(
            sell_amount, sell_gold, substep, state_history, prev_state
        )
        # TODO this has to happen hear to avoid circular referencing, find better solution
        self.parent.change_account_balance(
            self.account_id, deltas["cusd"], deltas["celo"], self.account_type
        )
        self.parent.change_reserve_account_balance(
            delta_cusd=deltas["cusd"], delta_celo=deltas["celo"]
        )
        return states
