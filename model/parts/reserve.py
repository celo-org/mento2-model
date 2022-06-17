"""
Reserve metric and advanced balance calculation
"""


from model.types.base import CryptoAsset


def p_reserve_statistics(
    _params,
    _substep,
    _state_history,
    prev_state,
):
    """
    calculates reserve statistics
    """
    reserve_values_usd = prev_state['reserve_balance'].values_in_usd(
        prev_state)
    reserve_balance_usd = sum(list(reserve_values_usd.values()))

    reserve_celo_usd = reserve_values_usd.get(CryptoAsset.CELO)

    floating_supply_values_usd = prev_state['floating_supply'].values_in_usd(
        prev_state)
    floating_supply_balance_usd = sum(list(floating_supply_values_usd.values()))

    reserve_ratio = reserve_celo_usd / floating_supply_balance_usd

    collateralisation_ratio = reserve_balance_usd / floating_supply_balance_usd

    return {
        'reserve_balance_in_usd': reserve_balance_usd,
        'floating_supply_stables_in_usd': floating_supply_balance_usd,
        'reserve_ratio': reserve_ratio,
        'collateralisation_ratio': collateralisation_ratio
    }
