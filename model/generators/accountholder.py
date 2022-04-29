"""
Provides Traders / Actors
"""
from abc import ABC, abstractmethod
from model.parts import buy_and_sell
from model.parts.strategies import TraderStrategyAbstract


from model.types import AccountType


# pylint: disable=too-few-public-methods


class AccountBase(ABC):
    """
    Agent / Account Holder
    """

    @abstractmethod
    def __init__(self, parent, account_id, account_name, balance, account_type=None):
        self.parent = parent
        self.account_id = account_id
        self.account_name = account_name
        self.balance = {"celo": balance["celo"], "cusd": balance["celo"]}
        self.account_type = account_type

    # TODO is this slowing down the simulation?
    @staticmethod
    def create_account_holder(parent, account_id, account_name, balance, account_type):
        """
        Creates an account
        """
        if account_type == AccountType.CONTRACT:
            account = Contract(parent, account_id, account_name, balance, account_type)
        elif account_type == AccountType.RANDOM_TRADER:
            account = AccountHolder(
                parent, account_id, account_name, balance, account_type
            )
        elif account_type == AccountType.MAX_TRADER:
            account = AccountHolder(
                parent, account_id, account_name, balance, account_type
            )
        elif account_type == AccountType.ARBITRAGE_TRADER:
            account = AccountHolder(
                parent, account_id, account_name, balance, account_type
            )
        return account


class AccountHolder(AccountBase):
    """
    Agent / Account Holder
    """

    def __init__(
        self, parent, account_id, account_name, balance, account_type, orders=None
    ):
        super().__init__(parent, account_id, account_name, balance, account_type)
        self.strategy = account_type.value(parent=self)
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
        if order is None:
            states = {
                "mento_buckets": prev_state["mento_buckets"],
                "floating_supply": prev_state["floating_supply"],
                "reserve_balance": prev_state["reserve_balance"],
                "mento_rate": prev_state["mento_rate"],
            }
        else:
            sell_amount = order["sell_amount"]
            sell_gold = order["sell_gold"]
            # print(self.balance,self.parent.reserve_account.balance)
            TraderStrategyAbstract.portfolio_balancing(
                self,
                sell_amount=sell_amount,
                sell_gold=sell_gold,
                prev_state=prev_state,
            )
            states, deltas = buy_and_sell.exchange(
                params, sell_amount, sell_gold, substep, state_history, prev_state
            )

            # TODO this has to happen here to avoid circular referencing, find better solution
            # deltas are from reserve perspective; (-1) to convert to trader perspective
            self.parent.change_account_balance(
                account_id=self.account_id,
                delta_celo=-deltas["celo"],
                delta_cusd=-deltas["cusd"],
                account_type=self.account_type,
            )
            self.parent.change_reserve_account_balance(delta_celo=deltas["celo"])
        return states


class Contract(AccountBase):
    """
    Smart Contract
    """

    def __init__(self, parent, account_id, account_name, balance, account_type):
        super().__init__(parent, account_id, account_name, balance, account_type)
