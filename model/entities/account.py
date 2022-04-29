"""
Account class acts as the base abstraction for a chain account
which holds balances.
"""
# pylint: disable=too-few-public-methods
from typing import TYPE_CHECKING
from uuid import UUID
from model.entities.balance import Balance
if TYPE_CHECKING:
    from model.generators.accounts import AccountGenerator

class Account():
    """
    Agent / Account Holder
    """
    parent: "AccountGenerator"
    account_id: UUID
    account_name: str
    balance: Balance

    def __init__(
        self,
        parent: "AccountGenerator",
        account_id: UUID,
        account_name: str,
        balance: Balance
    ):
        self.parent = parent
        self.account_id = account_id
        self.account_name = account_name
        self.balance = balance
