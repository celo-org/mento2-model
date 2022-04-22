"""
Accounts Generator

Account management, equivalent to addresses on the blockchain
"""

from functools import reduce
from typing import List, Dict
from uuid import UUID, uuid5
from model.entities.balance import Balance
from model.entities.trader import Trader
from model.types import TraderType

from model.generators.generator import Generator
# from model.generators.traders import AccountBase, AccountHolder
from model.entities.account import Account

class AccountGenerator(Generator):
    """
    AccountsManager Generator
    """
    accounts_by_id: Dict[UUID, Account]
    reserve: Account
    epoch_rewards: Account

    def __init__(self, reserve_inventory):
        # TODO number of accounts with different types
        self.total_number_of_accounts: Dict[TraderType, int] = {
            account_type: 0 for account_type in TraderType
        }
        self.all_accounts: Dict[TraderType, List[Account]] = {
            account_type: [] for account_type in TraderType
        }
        # reserve account with account_id=0
        self.reserve = self.create_reserve_account(
            initial_balance=Balance(**reserve_inventory)
        )
        # epoch rewards account with account_id=1
        self.epoch_rewards = self.create_new_account(
            account_name="epoch_rewards"
        )
        # TODO create fast calibration to have one trader for all floating supply
        # these variables get initialized and updated by their @property function
        self._total_supply_celo = self.total_supply_celo
        self._floating_supply_celo = self.floating_supply_celo
        self._floating_supply_cusd = self.floating_supply_cusd

    @classmethod
    def from_parameters(cls, params):
        accounts = cls(params["reserve_inventory"])

        for trader_type in params["traders"]:
            index = 0
            for index in range(params["traders"][trader_type]):
                accounts.create_trader(
                    account_name=f"{trader_type}_{index}",
                    initial_balance=Balance(celo=1000, cusd=10000),
                    trader_type=trader_type
                )
        return accounts

    def create_reserve_account(self, initial_balance: Balance):
        """
        separate reserve account which is not part of the self.all_accounts list
        """
        reserve_account = Account(
            self,
            account_id=uuid5("accounts", "reserve"),
            account_name="reserve",
            balance=initial_balance
        )
        return reserve_account

    def create_new_account(self, account_name):
        """
        Creates new account with zero balances
        """
        account = Account(
            self,
            account_id=uuid5("accounts", account_name),
            account_name=account_name,
            balance={"celo": 0, "cusd": 0},
        )
        self.accounts_by_id[account.account_id] = account
        return account

    def change_reserve_account_balance(self, delta: Balance):
        """
        changes reserve balance, which is not part of the self.all_accounts list
        """
        self.reserve.balance += delta

    def change_account_balance(self, account_id: UUID, delta: Balance):
        account = self.accounts_by_id.get(account_id, None)
        assert account is not None, f"No account with id {account_id}"
        account.balance += delta

    def create_trader(self, account_name: str, initial_balance: Balance, trader_type: TraderType):
        account = Trader(
            self,
            account_id=uuid5("accounts", account_name),
            account_name=account_name,
            balance=initial_balance,
            strategy=trader_type
        )
        self.accounts_by_id[account.account_id] = account
        return account

    @property
    def total_supply_celo(self):
        """
        sums up celo balances over all accounts
        """
        return self.floating_supply_celo + self.reserve.balance.celo

    @property
    def floating_supply_celo(self):
        """
        sums up celo balances over all accounts except reserve
        """
        return reduce(lambda s, account: s + account.balance.celo, self.accounts_by_id.items(), 0)

    @property
    def floating_supply_cusd(self) -> int:
        """
        sums up cusd balances over all accounts except reserve
        """
        return reduce(lambda s, account: s + account.balance.cusd, self.accounts_by_id.items(), 0)
