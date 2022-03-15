"""
# Accountrelated Update and Policy functions


"""
from model.generators.container import container
from model.generators.accounts import AccountGenerator, AccountType


#
# @container.inject(AccountGenerator)
# def p_create_accounts(
#     _params,
#     _substep,
#     _state_history,
#     _prev_state,
#     account_generator: AccountGenerator,
# ):
#     """
#     Creates Accounts
#     """
#     _temp = account_generator.reserve_account


#     return {'number_of_accounts': 0}


@container.inject(AccountGenerator)
def p_random_trading(
    params,
    substep,
    state_history,
    prev_state,
    account_generator: AccountGenerator,
):
    """
    Executes a random trade
    """
    # TODO only works with one trader. Otherwise the bucket sizes are not dynamically adjusted.
    # TODO How can we implement dynamic substeps
    traders = account_generator.all_accounts[AccountType.RANDOM_TRADER]
    trader = traders[0]
    return trader.execute(params, substep, state_history, prev_state)
