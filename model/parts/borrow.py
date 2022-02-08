"""
# Borrow-feature related policy and state update functions

More details here (TBD).
"""
import numpy as np
from model.parts.celo_system import AccountManager
from model.types import Account_id
from typing import TypedDict


# TODO: Should this live here?
# Never interact with an IRP object directly, always use the IRP Manager
class IRP:
    """
    Class for a single IRP
    """
    def __init__(self, account, celo_lend, cusd_borrowed):
        self.account = account
        self.celo_lend = celo_lend
        self.cusd_borrowed = cusd_borrowed
        self._liquidated = False

    def check_liquidated(self, celo_usd_price, liquidation_threshold):
        if self._liquidated:
            return True

        self._liquidated = self.celo_lend * celo_usd_price / self.cusd_borrowed > liquidation_threshold
        return self._liquidated


# TODO: Should this live here?
class IRPManager:
    def __init__(self):
        self.total_number_of_irps = 0
        self.all_irps: TypedDict[Account_id, IRP] = dict()
        self.total_celo_lend = 0
        self.total_cusd_borrowed = 0

    def create_new_irp(self, account_id, celo_lend, cusd_borrowed):
        account = account_manager.get_account(account_id)
        self.all_irps[account_id] = IRP(
                account=account,
                celo_lend=celo_lend,
                cusd_borrowed=cusd_borrowed
        )

        self.total_number_of_irps += 1

        # Update account balances
        account_manager.change_account_balance(
            account_id=account_id,
            delta_celo=-celo_lend,
            delta_cusd=cusd_borrowed
        )

        # Update total IRP metrics
        self.total_celo_lend += celo_lend
        self.total_cusd_borrowed += cusd_borrowed
        return account_id

    def check_irp_for_liquidation(self, account_id, celo_usd_price, liquidation_threshold):
        return self.all_irps[account_id](
            celo_usd_price=celo_usd_price,
            liquidation_threshold=liquidation_threshold
        )

    def check_all_irps_for_liquidation(self, celo_usd_price, liquidation_threshold):
        for account_id, irp in self.all_irps.keys():
            self.check_irp_for_liquidation(
                account_id=account_id,
                celo_usd_price=celo_usd_price,
                liquidation_threshold=liquidation_threshold
            )


# TODO: Where should the account manger instance live such that it is shared across all model parts?
account_manager = AccountManager()
irp_manager = IRPManager()


def p_create_random_irp(params, substep, state_history, prev_state):
    """
    Creates, with probability probability_of_new_irp_per_block, a new IRP
    """

    # TODO: Check this earlier if possible
    if not params['feature_borrow_and_repay_stables_enabled']:
        return {
            'total_celo_lend': prev_state['total_celo_lend'],
            'total_cusd_borrowed': prev_state['total_cusd_borrowed']
        }

    if np.random.uniform() > params['probability_of_new_irp_per_block']:
        return {
            'total_celo_lend': prev_state['total_celo_lend'],
            'total_cusd_borrowed': prev_state['total_cusd_borrowed']
        }

    new_account_id = account_manager.create_funded_account(
        celo=params['initial_irp_user_celo_balance'],
        cusd=0
    )

    celo_lend = params['initial_irp_user_celo_balance']  # TODO: Allow less than full balance amount

    # TODO: Should we really use the mento rate here or rather the CELO/USD rate?
    cusd_borrowed = (
            celo_lend * prev_state['mento_rate'] / params['initial_collateralization_ratio']
    )

    irp_manager.create_new_irp(
        account_id=new_account_id,
        celo_lend=celo_lend,
        cusd_borrowed=cusd_borrowed
    )

    total_celo_lend = prev_state['total_celo_lend'] + celo_lend
    total_cusd_borrowed = prev_state['total_cusd_borrowed'] + cusd_borrowed

    return {
        'total_celo_lend': total_celo_lend,
        'total_cusd_borrowed': total_cusd_borrowed
    }
