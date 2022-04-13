"""
Provides Traders / Actors
"""
from model.parts import buy_and_sell

from model.parts.strategy_random_trader import RandomTrading


#pylint: disable=too-few-public-methods
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
        self.strategy = RandomTrading(self)
        self.orders = orders

    def execute(
        self,
        params,
        substep,
        state_history,
        prev_state,
    ):
        """
        Making pylint happy
        """
        order = self.strategy.return_optimal_trade(params, prev_state)
        sell_amount = order["sell_amount"]
        sell_gold = order["sell_gold"]
        states, deltas = buy_and_sell.exchange(
            params, sell_amount, sell_gold, substep, state_history, prev_state
        )
        # TODO this has to happen here to avoid circular referencing, find better solution
        self.parent.change_account_balance(
            self.account_id, deltas["cusd"], deltas["celo"], self.account_type
        )
        self.parent.change_reserve_account_balance(delta_celo=deltas["celo"])
        return states
