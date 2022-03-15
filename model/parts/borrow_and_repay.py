"""
# Borrow-feature related policy and state update functions

More details here (TBD).
"""
from typing import TypedDict
from model.types import Account_id


# Never interact with an _IRP object directly, always use the _IRP Manager
class _IRP:
    """
    Class for a single IRP
    """
    def __init__(self, account, celo_deposited, cusd_borrowed):
        self.account = account
        self.celo_deposited = celo_deposited
        self.cusd_borrowed = cusd_borrowed
        self.celo_liquidated = 0
        self.cusd_uncollateralized = 0
        self.liquidated = False

    def undercollateralized(self, celo_usd_price, liquidation_threshold):
        if self.liquidated:
            return True  # Liquidated IRPs have no collateral so they are undercollateralized
        return self.cusd_borrowed / (self.celo_deposited * celo_usd_price) > liquidation_threshold

    def liquidate_if_undercollaterlized(self, celo_usd_price, liquidation_threshold):
        if not self.liquidated and self.undercollateralized(
            celo_usd_price=celo_usd_price,
            liquidation_threshold=liquidation_threshold
        ):
            self.celo_liquidated = self.celo_deposited  # TODO: Should this always be the full amount?
            self.celo_deposited = 0
            self.liquidated = True
            return self.celo_liquidated, self.cusd_borrowed
        else:
            return 0.0, 0.0


# TODO: Should this live here?
class IRPManager:
    def __init__(self, account_manager):
        self.all_irps: TypedDict[Account_id, _IRP] = dict()
        self.total_celo_deposited = 0
        self.total_celo_liquidated = 0
        self.total_cusd_borrowed = 0
        self.total_cusd_from_liquidated_irps = 0
        self.account_manager = account_manager

    def average_collateralization_ratio(self, celo_usd_price):
        return self.total_celo_deposited * celo_usd_price

    def create_new_irp(self, account_id, celo_lend, cusd_borrowed):
        account = self.account_manager.get_account(account_id)
        self.all_irps[account_id] = _IRP(
                account=account,
                celo_deposited=celo_lend,
                cusd_borrowed=cusd_borrowed
        )

        # Update account balances
        self.account_manager.change_account_balance(
            account_id=account_id,
            delta_celo=-celo_lend,
            delta_cusd=cusd_borrowed
        )

        # Update total _IRP metrics
        self.total_celo_deposited += celo_lend
        self.total_cusd_borrowed += cusd_borrowed
        return account_id

    def liquidate_irps_if_undercollaterlized(self, celo_usd_price, liquidation_threshold):
        if not self.all_irps:
            return  # No irps yet
        additional_celo_liquidated = 0
        additional_cusd_from_liquidated_irps = 0
        for account_id, irp in self.all_irps.items():
            celo_liquidated, cusd_uncollateralized = irp.liquidate_if_undercollaterlized(
                celo_usd_price=celo_usd_price,
                liquidation_threshold=liquidation_threshold
            )
            additional_celo_liquidated += celo_liquidated
            additional_cusd_from_liquidated_irps += cusd_uncollateralized

        self.total_celo_deposited -= additional_celo_liquidated
        self.total_celo_liquidated += additional_celo_liquidated
        self.total_cusd_borrowed -= additional_cusd_from_liquidated_irps
        self.total_cusd_from_liquidated_irps += additional_cusd_from_liquidated_irps

    def get_current_irp_totals(self):
        """
        You might want to trigger additional liquidations first via liquidate_irps_if_undercollaterlized
        """
        return (
            self.total_celo_deposited,
            self.total_cusd_borrowed,
            self.total_celo_liquidated,
            self.total_cusd_from_liquidated_irps
        )

    def reset(self, account_manager):
        self.__init__(
            account_manager=account_manager
        )
        print('irp_manager reset!')
