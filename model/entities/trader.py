"""
Agents extends accounts to implement behavior via strategies.
Agents implement the Actor type.
"""
# pylint: disable=too-few-public-methods
from typing import TYPE_CHECKING
from copy import deepcopy
from uuid import UUID

from model.generators.mento import MentoExchangeGenerator
from model.entities.strategies import TraderStrategy
from model.entities.account import Account, Balance
from model.types import Fiat, MentoExchangeConfig, TraderConfig

if TYPE_CHECKING:
    from model.generators.accounts import AccountGenerator

class Trader(Account):
    """
    The Trader extens an account with a trading strategy.
    """
    strategy: TraderStrategy
    config: TraderConfig
    exchange_config: MentoExchangeConfig
    mento: MentoExchangeGenerator

    def __init__(
        self,
        parent: "AccountGenerator",
        account_id: UUID,
        account_name: str,
        config: TraderConfig,
    ):
        super().__init__(parent, account_id, account_name, config.balance)
        self.mento = self.parent.container.get(MentoExchangeGenerator)
        self.strategy = config.trader_type.value(self)
        self.config = config
        self.exchange_config = self.mento.configs.get(self.config.exchange)

    def execute(
        self,
        params,
        prev_state,
    ):
        """
        Execute the agent's state change
        """
        order = self.strategy.return_optimal_trade(params, prev_state)
        if order is None:
            return {
                "mento_buckets": prev_state["mento_buckets"],
                "floating_supply": prev_state["floating_supply"],
                "reserve_balance": prev_state["reserve_balance"],
            }

        sell_amount = order["sell_amount"]
        sell_reserve_currency = order["sell_reserve_currency"]
        self.rebalance_portfolio(sell_amount, sell_reserve_currency, prev_state)

        next_bucket, delta = self.mento.exchange(
            self.config.exchange,
            sell_amount,
            sell_reserve_currency,
            prev_state
        )

        self.balance += delta
        reserve_delta = Balance.zero()
        reserve_delta.set(
            self.exchange_config.reserve_currency,
            -1 * delta.get(self.exchange_config.reserve_currency),
        )
        self.parent.reserve.balance += reserve_delta

        next_buckets = deepcopy(prev_state["mento_buckets"])
        next_buckets[self.config.exchange] = next_bucket

        return {
            "mento_buckets": next_buckets,
            "floating_supply": self.parent.floating_supply.__dict__,
            "reserve_balance": self.parent.reserve.balance.__dict__
        }

    def rebalance_portfolio(self, target_amount, target_is_reserve_currency, prev_state):
        """
        Sometimes the optimal trade might require selling more of an
        asset than the trader has in his portfolio, but the total
        value of the portfolio would cover it therefore they can
        rebalance and execute the trade.
        """
        reserve_currency = self.exchange_config.reserve_currency
        stable = self.exchange_config.stable

        # TODO: Should these be quoted in the specific
        # fiat of the stable?
        market_price = (
            prev_state["market_price"].get(reserve_currency).get(Fiat.USD)
            / prev_state("market_price").get(stable).get(Fiat.USD)
        )

        delta = Balance.zero()
        if target_is_reserve_currency and self.balance.get(reserve_currency) < target_amount:
            delta.set(stable, -1 * self.balance.get(stable))
            delta.set(reserve_currency, self.balance.get(stable) / market_price)
        elif (not target_is_reserve_currency) and self.balance.get(stable) < target_amount:
            delta.set(stable, self.balance.get(reserve_currency) * market_price)
            delta.set(reserve_currency, -1 * self.balance.get(reserve_currency))

        self.balance += delta
        self.parent.untracked_floating_supply -= delta
