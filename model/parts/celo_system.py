"""
# Celo System

General Celo blockchain mechanisms, such as updating the CELO supply through epoch rewards.
"""
import numpy as np
from model.types import Account
from typing import List


# TODO: Should this live here?
class AccountManager:
    def __init__(self):
        self.total_number_of_accounts = 0
        self.all_accounts: List[Account] = []
        self.total_celo_supply = 0
        self.total_cusd_supply = 0

    def create_new_account(self):
        account_id = self.total_number_of_accounts
        new_account = Account(
            account_id=account_id,
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
        # Adjust total supply
        self.total_celo_supply += delta_celo
        self.total_cusd_supply += delta_cusd

    def create_funded_account(self, celo, cusd):
        account_id = self.create_new_account()
        self.change_account_balance(account_id, celo, cusd)
        return account_id

    def get_account(self, account_id) -> Account:
        self.check_account_valid(account_id)
        return self.all_accounts[account_id]

    def check_account_valid(self, account_id):
        assert len(self.all_accounts) > 0, ' No accounts exist'
        assert self.all_accounts[account_id]['account_id'] == account_id, 'Account_id mismatch'
