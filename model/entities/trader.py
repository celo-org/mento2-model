"""
Agents extends accounts to implement behavior via strategies.
Agents implement the Actor type.
"""
# pylint: disable=too-few-public-methods
from typing import Type, TYPE_CHECKING
from uuid import UUID
from model.parts.strategies import TraderStrategyAbstract
from model.parts.buy_and_sell import exchange
from model.entities.account import Account, Balance

if TYPE_CHECKING:
    from model.generators.accounts import AccountGenerator

class Trader(Account):
    """
    The Trader extens an account with a trading strategy.
    """
    strategy: TraderStrategyAbstract

    def __init__(
        self,
        parent: "AccountGenerator",
        account_id: UUID,
        account_name: str,
        balance: Balance,
        strategy: Type[TraderStrategyAbstract]
    ):
        super().__init__(parent, account_id, account_name, balance)
        self.strategy = strategy(self)

    def execute(
        self,
        params,
        substep,
        state_history,
        prev_state,
    ):
        """
        Execute the agent's state change
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
            states, deltas = exchange(
                params, sell_amount, sell_gold, substep, state_history, prev_state
            )
            # TODO this has to happen here to avoid circular referencing, find better solution
            self.parent.get(self.account_id).balance += Balance(**deltas)
            self.parent.reserve.balance += Balance(celo=deltas["celo"], cusd=0)
        return states
