import numpy as np
from model.parts.buy_and_sell import BuyAndSellManager
from model.parts.actors import ActorManager
from model.parts.celo_system import AccountManager
from model.parts.borrow_and_repay import IRPManager
from model.parts.strategies import SellMax

# Initialize managers and strategies
account_manager = AccountManager()
buy_and_sell_manager = BuyAndSellManager()
actor_manager = ActorManager(
    account_manager=account_manager,
    buy_and_sell_manager=buy_and_sell_manager
)
irp_manager = IRPManager(
    account_manager=account_manager
)
sell_max_strategy = SellMax(
    acting_frequency=12*60*24,  # once a day, TODO: Make this a parameter
    buy_and_sell_manager=buy_and_sell_manager
)


def p_random_celo_usd_price_change(params, substep, state_history, prev_state):
    """
    Create some random changes in celo_usd_price
    """
    vola_per_block = 5.0 / np.sqrt(365*24*60*12)  # Annual vola of 500% for some action
    pct_change = np.random.normal() * vola_per_block
    return {
        'celo_usd_price': prev_state['celo_usd_price'] * np.exp(pct_change)
    }


def p_bucket_update(params, substep, state_history, prev_state):
    """
    Only update buckets every update_frequency_seconds
    """

    # TODO: Check this earlier if possible / use decorator
    if not buy_and_sell_manager.buy_and_sell_feature_enabled(params):
        return buy_and_sell_manager.leave_all_state_variables_unchanged(
            prev_state=prev_state,
            policy_type='bucket_update'
        )

    if buy_and_sell_manager.buckets_should_be_reset(
            params=params, prev_state=prev_state
    ):
        return buy_and_sell_manager.calculate_reset_buckets(
            params=params, prev_state=prev_state
        )

    else:
        return buy_and_sell_manager.leave_all_state_variables_unchanged(
            prev_state=prev_state,
            policy_type='bucket_update'
        )


def p_create_random_irp(params, substep, state_history, prev_state):
    """
    Creates, with probability probability_of_new_irp_per_block, a new _IRP
    """

    # TODO: Check this earlier if possible / do this with a decorator
    if not params['feature_borrow_and_repay_stables_enabled']:
        return {
            'total_celo_deposited': prev_state['total_celo_deposited'],
            'total_cusd_borrowed': prev_state['total_cusd_borrowed']
        }

    # Do this via generators instead
    if len(state_history) == 1:
        irp_manager.reset(
            account_manager=account_manager
        )

    if np.random.uniform() > params['probability_of_new_irp_per_block']:
        return {
            'total_celo_deposited': prev_state['total_celo_deposited'],
            'total_cusd_borrowed': prev_state['total_cusd_borrowed']
        }

    celo_lend = params['initial_irp_user_celo_balance']  # TODO: Allow less than full balance amount

    # TODO: Should we really use the CELO/USD rate here or rather the mento rate?
    cusd_borrowed = (
            celo_lend * prev_state['celo_usd_price'] / params['initial_collateralization_ratio']
    )

    # Initialize a new, funded account for _IRP creator
    new_account_id = account_manager.create_funded_account(
        celo=params['initial_irp_user_celo_balance'],
        cusd=0
    )

    irp_manager.create_new_irp(
        account_id=new_account_id,
        celo_lend=celo_lend,
        cusd_borrowed=cusd_borrowed
    )

    total_celo_lend = prev_state['total_celo_deposited'] + celo_lend
    total_cusd_borrowed = prev_state['total_cusd_borrowed'] + cusd_borrowed

    return {
        'total_celo_deposited': total_celo_lend,
        'total_cusd_borrowed': total_cusd_borrowed
    }


def p_liquidate_undercollateralized_irps(params, substep, state_history, prev_state):
    """
    Liquidates all IRPs that are below the liquidation threshold
    """
    # TODO: Check this earlier if possible / do this with a decorator
    if not params['feature_borrow_and_repay_stables_enabled']:
        return {
            'total_celo_deposited': prev_state['total_celo_deposited'],
            'total_cusd_borrowed': prev_state['total_cusd_borrowed'],
            'total_celo_liquidated': prev_state['total_celo_liquidated'],
            'total_cusd_from_liquidated_irps': prev_state['total_cusd_from_liquidated_irps']
        }

    irp_manager.liquidate_irps_if_undercollaterlized(
        celo_usd_price=prev_state['celo_usd_price'],
        liquidation_threshold=params['liquidation_threshold']
    )
    total_celo_deposited, total_cusd_borrowed, total_celo_liquidated, total_cusd_from_liquidated_irps = (
            irp_manager.get_current_irp_totals()
    )

    return {
        'total_celo_deposited': total_celo_deposited,
        'total_cusd_borrowed': total_cusd_borrowed,
        'total_celo_liquidated': total_celo_liquidated,
        'total_cusd_from_liquidated_irps': total_cusd_from_liquidated_irps
    }


def p_actors_act(params, substep, state_history, prev_state):
    # TODO: Allow this for more than one actor
    # TODO: Use generator logic instead len==1 check
    # Only create one buy_and_sell_arb actor per parameter set
    if len(state_history) == 1:
        actor_manager.reset(
            sell_max_strategy=sell_max_strategy
        )

    state_variables_after_actors_acted = actor_manager.all_actors[0].strategy.execute_optimal_action(
        params=params, prev_state=prev_state
    )

    return state_variables_after_actors_acted
