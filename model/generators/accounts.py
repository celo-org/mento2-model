"""
Accounts Generator

Account management, equivalent to addresses on the blockchain
"""


from enum import Enum
from typing import List, Dict

from model.generators.generator import Generator
from model.generators.traders import AccountHolder

# from data.historical_values import (
#    celo_supply_mean,
#    cusd_supply_mean,
# )


class AccountType(Enum):
    ARB_TRADER = "arb_trader"
    RANDOM_TRADER = "random_trader"
    CONTRACT = "contract"


class AccountGenerator(Generator):
    """
    AccountsManager Generator
    """

    def __init__(self, reserve_inventory):
        # TODO number of accounts with different types
        self.total_number_of_accounts: Dict[AccountType, int] = {
            account_type: 0 for account_type in AccountType
        }
        self.all_accounts: Dict[AccountType, List[AccountHolder]] = {
            account_type: [] for account_type in AccountType
        }

        self.create_reserve_account(reserve_inventory)
        # TODO create fast calibration to have one trader for all floating supply
        # self.create_funded_account(account_name='random_trader', celo=1000, cusd=10000)
        # self.create_funded_account(account_name='floating_supply_placeholder',
        #                            celo=celo_supply_mean
        #                                 - self.get_account(0)['celo']
        #                                 - self.get_account(1)['celo'],
        #                            cusd=cusd_supply_mean
        #                                 - self.get_account(1)['cusd'])

        self.total_supply_celo = self.get_total_supply_celo()
        self.total_supply_cusd = self.get_total_supply_cusd()
        self.floating_supply_celo = self.get_floating_supply_celo()
        self.floating_supply_cusd = self.get_floating_supply_cusd()

    @classmethod
    def from_parameters(cls, params):
        # Init reserve, floating supply account, mento account here
        accounts = cls(params["reserve_inventory"])

        for account_type in AccountType:
            index = 0
            for index in range(params["number_of_accounts"][account_type]):
                accounts.create_funded_account(
                    account_name=f"{account_type.value}_{index}",
                    celo=1000,
                    cusd=10000,
                    account_type=account_type,
                )
        return accounts

    def create_reserve_account(self, reserve_inventory):
        self.reserve_account = AccountHolder(
            self,
            account_id=0,
            account_name="reserve",
            balance={
                "celo": reserve_inventory["celo"],
                "cusd": reserve_inventory["cusd"],
            },
            account_type=AccountType.CONTRACT,
        )
        # TODO Reserve account as first contract account???

    def create_new_account(self, account_name, account_type):
        """
        Creates new account with zero balances
        """
        account_id = self.total_number_of_accounts[account_type]
        new_account = AccountHolder(
            self,
            account_id=account_id,
            account_name=account_name,
            balance={"celo": 0, "cusd": 0},
            account_type=account_type,
        )
        self.all_accounts[account_type].append(new_account)
        self.total_number_of_accounts[account_type] += 1
        return account_id

    def change_reserve_account_balance(
        self, delta_celo, delta_cusd):
        #TODO check for reserve account
        #self.check_account_valid(account_id, account_type)
        self.reserve_account.balance["celo"] += delta_celo
        self.reserve_account.balance["cusd"] += delta_cusd
    def change_account_balance(
        self, account_id, delta_celo, delta_cusd, account_type: AccountType
    ):
        self.check_account_valid(account_id, account_type)
        self.all_accounts[account_type][account_id].balance["celo"] += delta_celo
        self.all_accounts[account_type][account_id].balance["cusd"] += delta_cusd

    def create_funded_account(self, account_name, celo, cusd, account_type):
        account_id = self.create_new_account(account_name, account_type)
        self.change_account_balance(account_id, celo, cusd, account_type)
        return account_id

    def get_account(self, account_id, account_type):  # -> Account:
        self.check_account_valid(account_id, account_type)
        return self.all_accounts[account_type][account_id]

    def check_account_valid(self, account_id, account_type):
        assert len(self.all_accounts[account_type]) > 0, " No accounts exist"
        assert (
            self.all_accounts[account_type][account_id].account_id == account_id
        ), "Account_id mismatch"

    def get_total_supply_celo(self):
        """
        sums up celo balances over all accounts
        """
        return self.get_floating_supply_celo() + self.reserve_account.balance["celo"]

    def get_floating_supply_celo(self):
        """
        sums up celo balances over all accounts except reserve
        """
        floating_supply = 0
        for account_type in AccountType:
            floating_supply = +sum(
                account.balance["celo"] for account in self.all_accounts[account_type]
            )
        return floating_supply

    def get_total_supply_cusd(self):
        """
        sums up cusd balances over all accounts
        """
        return self.get_floating_supply_cusd() + self.reserve_account.balance["cusd"]

    def get_floating_supply_cusd(self):
        """
        sums up cusd balances over all accounts except reserve
        """
        floating_supply = 0
        for account_type in AccountType:
            floating_supply = +sum(
                account.balance["cusd"] for account in self.all_accounts[account_type]
            )
        return floating_supply
