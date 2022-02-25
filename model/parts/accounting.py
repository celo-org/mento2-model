"""
# Accountrelated Update and Policy functions


"""
from model.generators.container import container
from model.generators.accounts import AccountGenerator


@container.inject(AccountGenerator)
def p_create_accounts(
    _params,
    _substep,
    _state_history,
    _prev_state,
    account_generator: AccountGenerator,
):
    """
    Creates Accounts
    """
    _temp = account_generator.reserve_account


    return {'number_of_accounts': 0}
