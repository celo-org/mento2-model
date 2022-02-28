"""
Accounts Generator

Account management, equivalent to addresses on the blockchain
"""

from typing import List
from model.types import Account
from model.generators.generator import Generator
from data.historical_values import (
    celo_supply_mean,
    cusd_supply_mean,
)


class AccountGenerator(Generator):
    """
    AccountsManager Generator
    """

    def __init__(self):
        self.total_number_of_accounts = 0
        self.all_accounts: List[Account] = []

        # create initial accounts
        self.create_funded_account(account_name='reserve', celo=120000000.0, cusd=0.0)
        self.create_funded_account(account_name='random_trader', celo=1000, cusd=10000)
        self.create_funded_account(account_name='floating_supply_placeholder',
                                   celo=celo_supply_mean
                                        - self.get_account(0)['celo']
                                        - self.get_account(1)['celo'],
                                   cusd=cusd_supply_mean
                                        - self.get_account(1)['cusd'])

        self.total_supply_celo = self.get_total_supply_celo()
        self.total_supply_cusd = self.get_total_supply_cusd()
        self.floating_supply_celo = self.get_floating_supply_celo()
        self.floating_supply_cusd = self.get_floating_supply_cusd()

    @classmethod
    def from_parameters(cls, params) -> "AccountsGenerator":
        # Init reserve, floating supply account, mento account here
        return cls()

    def create_new_account(self, account_name):
        """
        Creates new account with zero balances
        """
        account_id = self.total_number_of_accounts
        new_account = Account(
            account_id=account_id,
            account_name=account_name,
            celo=0,
            cusd=0
        )
        self.all_accounts.append(new_account)
        self.total_number_of_accounts += 1
        return account_id

    def change_account_balance(self, account_id, delta_celo, delta_cusd):
        self.check_account_valid(account_id)
        self.all_accounts[account_id]['celo'] += delta_celo
        self.all_accounts[account_id]['cusd'] += delta_cusd

    def create_funded_account(self, account_name, celo, cusd):
        account_id = self.create_new_account(account_name)
        self.change_account_balance(account_id, celo, cusd)
        return account_id

    def get_account(self, account_id) -> Account:
        self.check_account_valid(account_id)
        return self.all_accounts[account_id]

    def check_account_valid(self, account_id):
        assert len(self.all_accounts) > 0, ' No accounts exist'
        assert self.all_accounts[account_id]['account_id'] == account_id, 'Account_id mismatch'

    def get_total_supply_celo(self):
        """
        sums up celo balances over all accounts
        """
        return float(sum([account['celo'] for account in self.all_accounts]))

    def get_floating_supply_celo(self):
        """
        sums up celo balances over all accounts except reserve
        """
        return float(sum([account['celo'] for account in self.all_accounts])
                     - self.get_account(0)['celo'])

    def get_total_supply_cusd(self):
        """
        sums up cusd balances over all accounts
        """
        return float(sum([account['cusd'] for account in self.all_accounts]))

    def get_floating_supply_cusd(self):
        """
        sums up cusd balances over all accounts except reserve
        """
        return float(sum([account['cusd'] for account in self.all_accounts])
                     - self.get_account(0)['cusd'])
