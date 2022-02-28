"""
Provides Traders / Actors
"""

#from abc import ABC, abstractclassmethod


import numpy as np
from experiments import simulation_configuration
from model.generators.temp_mento import exchange


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

    def execute(self, params, substep, state_history, prev_state):
        sell_amount = self.orders["sell_amount"][prev_state["timestep"]]
        sell_gold = self.orders["sell_gold"][prev_state["timestep"]]
        states, deltas = exchange(
            sell_amount, sell_gold, params, substep, state_history, prev_state
        )
        self.parent.change_account_balance(
            self.account_id, deltas["cusd"], deltas["celo"], self.account_type
        )
        return states


# # pylint: disable=too-few-public-methods
# class Trader(ABC):
#     """
#     Abstract Generator class, this is very light at the moment
#     but might grow if we discover patterns in Generators that
#     are worth abstracting, either way having this is helpful
#     for the type system.
#     """

#     def __init__(
#         self, parent, account_id, account_name, balance, account_type=None, orders=None
#     ):
#         self.parent = parent
#         self.account_id = account_id
#         self.account_name = account_name
#         self.balance = {"celo": balance["celo"], "cusd": balance["celo"]}
#         self.account_type = account_type
#         self.dummy = 0
#         self.orders = orders

#     def execute(
#         self, parent, account_id, account_name, balance, account_type=None, orders=None
#     ):
#         pass


# class ArbTrader(Trader):
#     def __init__():
