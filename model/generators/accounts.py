"""
Accounts Generator

Account management, equivalent to addresses on the blockchain
"""
from uuid import UUID, uuid4, uuid5
from typing import List, Dict

from model.entities.account import Account
from model.entities.trader import Trader
from model.entities.balance import Balance
from model.config_types import TraderConfig
from model.utils import update_from_signal
from model.utils.generator import Generator, state_update_blocks
from model.utils.generator_container import GeneratorContainer

ACCOUNTS_NS = uuid4()


class AccountGenerator(Generator):
    """
    AccountsManager Generator
    """
    accounts_by_id: Dict[UUID, Account] = {}
    reserve: Account
    # Holds the amount of floating supply in circulation
    # with entities that aren't tracked as part of the
    # generator.
    untracked_floating_supply: Balance
    container: GeneratorContainer

    def __init__(self,
                 reserve_inventory: Balance,
                 initial_floating_supply: Balance,
                 traders: List[TraderConfig],
                 container: GeneratorContainer):
        self.container = container
        self.reserve = self.create_reserve_account(
            initial_balance=reserve_inventory
        )

        for trader in traders:
            for index in range(trader.count):
                self.create_trader(
                    account_name=f"{trader.trader_type}_{index}",
                    config=trader
                )

        self.untracked_floating_supply = initial_floating_supply - self.tracked_floating_supply

    @classmethod
    def from_parameters(cls, params, initial_state, container):
        accounts = cls(
            Balance(params["reserve_inventory"]),
            Balance(initial_state["floating_supply"]),
            params["traders"],
            container,
        )

        return accounts

    def create_reserve_account(self, initial_balance: Balance):
        """
        separate reserve account which is not part of the self.all_accounts list
        """
        reserve_account = Account(
            self,
            account_id=uuid5(ACCOUNTS_NS, "reserve"),
            account_name="reserve",
            balance=initial_balance
        )
        return reserve_account

    def create_trader(self, account_name: str, config: TraderConfig):
        account = Trader(
            self,
            account_id=uuid5(ACCOUNTS_NS, account_name),
            account_name=account_name,
            config=config
        )
        self.accounts_by_id[account.account_id] = account
        return account

    @state_update_blocks("traders")
    def traders_execute(self):
        return [
            {
                "description": f"""
                    Trader update blocks for {trader.account_id}
                """,
                "policies": {
                    "trader_policy": self.get_trader_policy(trader.account_id)
                },
                "variables": {
                    "mento_buckets": update_from_signal("mento_buckets"),
                    "reserve_balance": update_from_signal("reserve_balance"),
                    "floating_supply": update_from_signal("floating_supply"),
                },
            } for trader in self.traders()
        ]

    def get_trader_policy(self, account_id):
        def policy(params, _substep, _state_history, prev_state):
            trader = self.get(account_id)
            return trader.execute(params, prev_state)
        return policy

    def traders(self) -> List[Trader]:
        return [
            account
            for account in self.accounts_by_id.values()
            if isinstance(account, Trader)
        ]

    def get(self, account_id) -> Account:
        account = self.accounts_by_id.get(account_id)
        assert account is not None, f"No account with id: {account_id}"
        return account

    @property
    def tracked_floating_supply(self) -> Balance:
        """
        Tracked floating supply which originates from
        """
        return sum(
            [account.balance for account in self.accounts_by_id.values()],
            Balance.zero()
        )

    @property
    def floating_supply(self) -> Balance:
        """
        Return the celo and cusd floating supply taking into account
        what's granularly tracked in the generator and what lives as
        untracked supply.
        """
        return self.tracked_floating_supply + self.untracked_floating_supply
