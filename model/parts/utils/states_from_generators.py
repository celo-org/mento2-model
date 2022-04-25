"""
Pipe data that lives in generators into state variables
"""
from lib.generator_container import inject
from model.generators.accounts import AccountGenerator
from model.types import AccountType


@inject(AccountGenerator)
def p_state_variables_from_generators(_params, _substep, _state_history, _prev_state,
                                      account_generator: AccountGenerator):
    """
    Policy function which updates state variables from generator objects
    """
    floating_supply = {
        'celo': account_generator.floating_supply_celo,
        'cusd': account_generator.floating_supply_cusd
    }
    reserve_balance = {
        'celo': account_generator.get_account(account_id=0,
                                              account_type=AccountType.CONTRACT).balance["celo"],
        'cusd':  account_generator.get_account(account_id=0,
                                               account_type=AccountType.CONTRACT).balance["cUSD"],
    }

    return {
        'reserve_balance': reserve_balance,
        'floating_supply': floating_supply
    }
