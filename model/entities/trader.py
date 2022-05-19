"""
Agents extends accounts to implement behavior via strategies.
Agents implement the Actor type.
"""
# pylint: disable=too-few-public-methods
import logging
from typing import Type, TYPE_CHECKING
from uuid import UUID
from model.parts.buy_and_sell import exchange
from model.entities.strategies import TraderStrategy
from model.entities.account import Account, Balance

if TYPE_CHECKING:
    from model.generators.accounts import AccountGenerator


class Trader(Account):
    """
    The Trader extens an account with a trading strategy.
    """
    strategy: TraderStrategy

    def __init__(
        self,
        parent: "AccountGenerator",
        account_id: UUID,
        account_name: str,
        balance: Balance,
        strategy: Type[TraderStrategy]
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
        logging.info(self.balance)
        order = self.strategy.return_optimal_trade(params, prev_state)
        if order is None:
            return dict(
                mento_buckets=prev_state["mento_buckets"],
                floating_supply=prev_state["floating_supply"],
                reserve_balance=prev_state["reserve_balance"],
            )

        sell_amount = order["sell_amount"]
        sell_gold = order["sell_gold"]
        self.rebalance_portfolio(sell_amount, sell_gold, prev_state)

        mento_buckets, deltas = exchange(
            params, sell_amount, sell_gold, substep, state_history, prev_state
        )

        self.balance += Balance(**deltas)
        self.parent.reserve.balance += Balance(celo=-deltas["celo"], cusd=0)

        return dict(
            mento_buckets=mento_buckets,
            floating_supply=self.parent.floating_supply.__dict__,
            reserve_balance=self.parent.reserve.balance.__dict__)

    def rebalance_portfolio(self, target_amount, target_is_celo, prev_state):
        """
        Sometimes the optimal trade might require selling more of an
        asset than the trader has in his portfolio, but the total
        value of the portfolio would cover it therefore they can
        rebalance and execute the trade.
        """
        price_celo_cusd = (
            prev_state["market_price"]["celo_usd"]
            / prev_state["market_price"]["cusd_usd"]
        )
        delta = Balance.zero()
        if target_is_celo and self.balance.celo < target_amount:
            delta = Balance(
                cusd=-self.balance.cusd,
                celo=self.balance.cusd / price_celo_cusd
            )
        elif (not target_is_celo) and self.balance.cusd < target_amount:
            delta = Balance(
                cusd=self.balance.celo * price_celo_cusd,
                celo=-self.balance.celo
            )

        self.balance += delta
        self.parent.untracked_floating_supply -= delta
