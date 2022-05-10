"""
Accounts Generator

Account management, equivalent to addresses on the blockchain
"""
from uuid import UUID, uuid4, uuid5
from typing import List, Dict
from functools import reduce

from model.entities.account import Account
from model.entities.trader import Trader
from model.entities.balance import Balance
from model.types import TraderType
from model.utils import update_from_signal
from model.utils.generator import Generator, state_update_blocks

ACCOUNTS_NS = uuid4()

class AccountGenerator(Generator):
    """
    AccountsManager Generator
    """
    accounts_by_id: Dict[UUID, Account] = {}
    reserve: Account
    epoch_rewards: Account

    def __init__(self, reserve_inventory):
        # TODO number of accounts with different types
        self.total_number_of_accounts: Dict[TraderType, int] = {
            account_type: 0 for account_type in TraderType
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

        for (trader_type, trader_params) in params["traders"].items():
            for index in range(trader_params["count"]):
                accounts.create_trader(
                    account_name=f"{trader_type}_{index}",
                    initial_balance=trader_params["balance"],
                    trader_type=trader_type
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

    def create_new_account(self, account_name):
        """
        Creates new account with zero balances
        """
        account = Account(
            self,
            account_id=uuid5(ACCOUNTS_NS, account_name),
            account_name=account_name,
            balance=Balance(celo=0, cusd=0),
        )
        self.accounts_by_id[account.account_id] = account
        return account

    def create_trader(self, account_name: str, initial_balance: Balance, trader_type: TraderType):
        account = Trader(
            self,
            account_id=uuid5(ACCOUNTS_NS, account_name),
            account_name=account_name,
            balance=initial_balance,
            strategy=trader_type.value,
        )
        self.accounts_by_id[account.account_id] = account
        return account

    @state_update_blocks("checkpoint")
    def checkpoint_state_update_blocks(self):
        return [{
            "description": """
            Checkpoint accounts generator totals to simulation state
            """,
            'policies': {
                'state_variables_from_generators': self.checkpoint_policy()
            },
            'variables': {
                'reserve_balance': update_from_signal('reserve_balance'),
                'floating_supply': update_from_signal('floating_supply')
            }
        }]

    def checkpoint_policy(self):
        """
        Policy function which updates state variables from generator objects
        """
        def _(_params, _substep, _state_history, _prev_state):
            floating_supply = {
                'celo': self.floating_supply_celo,
                'cusd': self.floating_supply_cusd
            }
            reserve_balance = {
                'celo': self.reserve.balance.celo,
                'cusd':  self.reserve.balance.cusd,
            }

            return {
                'reserve_balance': reserve_balance,
                'floating_supply': floating_supply
            }
        return _

    @state_update_blocks("traders")
    def all_trader_state_update_blocks(self):
        return [
            {
                "description": f"""
                    Trader update blocks for {trader.account_id}
                """,
                "policies": {
                    "random_trade": self.trader_policy(trader.account_id)
                },
                "variables": {
                    "mento_buckets": update_from_signal("mento_buckets"),
                    "reserve_balance": update_from_signal("reserve_balance"),
                    "floating_supply": update_from_signal("floating_supply"),
                },

            } for trader in self.traders()
        ]

    def traders(self) -> List[Trader]:
        return filter(lambda account: isinstance(account, Trader), self.accounts_by_id.values())

    def trader_policy(self, account_id):
        def policy(params, substep, state_history, prev_state):
            trader = self.accounts_by_id[account_id]
            return trader.execute(params, substep, state_history, prev_state)
        return policy

    def get(self, account_id) -> Account:
        account = self.accounts_by_id.get(account_id)
        assert account is not None, f"No account with id: {account_id}"
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
        return reduce(lambda s, account: s + account.balance.celo, self.accounts_by_id.values(), 0)

    @property
    def floating_supply_cusd(self) -> int:
        """
        sums up cusd balances over all accounts except reserve
        """
        return reduce(lambda s, account: s + account.balance.cusd, self.accounts_by_id.values(), 0)
