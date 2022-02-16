"""
# Mento1 related policy and state update functions

Calculation of changes in Mento buckets sizes, floating supply and reserve balances.
"""

import numpy as np
from model.constants import blocktime_seconds
from model.types import Token_balance
from actors import ActorManager


# TODO: Should this live here?
class Trade:
    """
    Class for trades happening in the buy and sell feature. Trades are always given from the perspective of the
    trader, i.e. if sell_gold=True then the trader sells CELO to the reserve. Amounts are always positive, deltas
    can be negative or positive
    """
    def __init__(self, sell_gold, sell_amount, buy_amount):
        # TODO: Add trader account id and checks against the respective balances
        self.sell_gold: bool = sell_gold
        self.sell_amount: Token_balance = sell_amount
        self.buy_amount: Token_balance = buy_amount

    @property
    def delta_trader_celo(self):
        """
        Celo delta from the perspective of the trader, i.e. if trader_delta_celo is negative, then the trader is
        selling CELO to the reserve for stables
        """
        if self.sell_gold:
            return -self.sell_amount
        else:
            return self.buy_amount

    @property
    def delta_trader_cusd(self):
        """
        cUSD delta from the perspective of the trader, i.e. if trader_delta_cusd is negative, then the trader is
        selling cUSD to the reserve for stables
        """
        if self.sell_gold:
            return self.buy_amount
        else:
            return -self.sell_amount

    @property
    def delta_reserve_celo(self):
        """
        Celo delta from the perspective of the reserve
        """
        return -self.delta_trader_celo

    @property
    def delta_reserve_cusd(self):
        """
        cUSD delta from the perspective of the reserve
        """
        return -self.delta_trader_celo

    @property
    def delta_float_celo(self):
        """
        Changes in float CELO
        """
        return self.delta_trader_celo

    @property
    def delta_float_cusd(self):
        """
        Changes in float cUSD
        """
        return self.delta_trader_cusd

    @property
    def delta_mento_bucket_celo(self):
        """
        Changes in float CELO
        """
        return -self.delta_trader_celo

    @property
    def delta_mento_bucket_cusd(self):
        """
        Changes in float cUSD
        """
        return -self.delta_trader_cusd


# TODO: Should this live here?
class BuyAndSellManager:
    def __init__(self):
        self.total_celo_bought = 0
        self.total_celo_sold = 0
        self.total_cusd_bought = 0
        self.total_cusd_sold = 0

    @staticmethod
    def leave_all_state_variables_unchanged(prev_state, policy_type):
        if policy_type == 'p_random_exchange':
            return {
                'mento_buckets': prev_state['mento_buckets'],
                'floating_supply': prev_state['floating_supply'],
                'reserve_balance': prev_state['reserve_balance'],
                'mento_rate': prev_state['mento_rate']
            }
        elif policy_type == 'p_bucket_update':
            return {
                'mento_buckets': prev_state['mento_buckets']
            }

    @staticmethod
    def buy_and_sell_feature_enabled(params):
        return params['feature_buy_and_sell_stables_enabled']

    @staticmethod
    def buckets_should_be_reset(params, prev_state):
        return (blocktime_seconds * prev_state['timestep']) % params['bucket_update_frequency_seconds'] == 0

    @staticmethod
    def calculate_reset_buckets(params, prev_state):
        celo_bucket = params['reserve_fraction'] * prev_state['reserve_balance']['celo']
        cusd_bucket = prev_state['celo_usd_price'] * celo_bucket
        mento_buckets = {
            'cusd': cusd_bucket,
            'celo': celo_bucket
        }
        return {
            'mento_buckets': mento_buckets
        }

    @staticmethod
    def _get_random_sell_fraction(params):
        return np.random.rand() * params['max_sell_fraction_of_float']

    @staticmethod
    def calculate_buy_amount_constant_product_amm(params, prev_state, sell_amount, sell_gold, min_buy_amount=0):
        spread = params['spread']
        reduced_sell_amount = sell_amount * (1 - spread)

        if sell_gold:
            buy_token_bucket = prev_state['mento_buckets']['cusd']
            sell_token_bucket = prev_state['mento_buckets']['celo']
        else:
            buy_token_bucket = prev_state['mento_buckets']['celo']
            sell_token_bucket = prev_state['mento_buckets']['cusd']

        numerator = sell_amount * (1 - spread) * buy_token_bucket
        denominator = sell_token_bucket + reduced_sell_amount
        buy_amount = numerator / denominator

        if buy_amount < min_buy_amount:
            buy_amount = np.nan

        return buy_amount

    def create_random_trade(self, params, prev_state):
        """
        Trade are given from perspective of a trader, i.e. sell_gold=True means a trader sells CELO to the reserve
        """
        sell_fraction = self._get_random_sell_fraction(params)
        sell_gold = np.random.rand() > 0.5
        if sell_gold:
            sell_amount = sell_fraction * prev_state['floating_supply']['celo']
        else:
            sell_amount = sell_fraction * prev_state['floating_supply']['cusd']

        buy_amount = self.calculate_buy_amount_constant_product_amm(
            params=params,
            prev_state=prev_state,
            sell_amount=sell_amount,
            sell_gold=sell_gold
        )

        trade = self.create_trade(
            sell_gold=sell_gold,
            sell_amount=sell_amount,
            buy_amount=buy_amount
        )

        return trade

    @staticmethod
    def create_trade(sell_gold, sell_amount, buy_amount):
        """
        Trade are given from perspective of a trader, i.e. sell_gold=True means a trader sells CELO to the reserve
        """
        trade = Trade(
            sell_gold=sell_gold,
            sell_amount=sell_amount,
            buy_amount=buy_amount
        )
        return trade

    @staticmethod
    def state_variables_state_after_trade(prev_state, trade):
        """
        Trades and deltas are given from perspective of a trader, i.e. sell_gold=True means a trader
        has a negative delta_celo
        """

        # TODO: Update the balance of a trader!

        # Mento buckets are virtual so they do not count neither to floating supply nor to the reserve balance
        mento_buckets = {
            'cusd': prev_state['mento_buckets']['cusd'] + trade.delta_mento_bucket_cusd,
            'celo': prev_state['mento_buckets']['celo'] + trade.delta_mento_bucket_celo
        }

        # If trader has positive delta, floating supply delta is positive (trader balance is part of float)
        floating_supply = {
            'cusd': prev_state['floating_supply']['cusd'] + trade.delta_float_cusd,
            'celo': prev_state['floating_supply']['celo'] + trade.delta_float_celo
        }

        # Redeemed cUSD are burned by the reserve
        reserve_account = {
            'celo': prev_state['reserve_balance']['celo'] + trade.delta_reserve_celo
        }

        mento_rate = mento_buckets['cusd'] / mento_buckets['celo']

        return {
            'mento_buckets': mento_buckets,
            'floating_supply': floating_supply,
            'reserve_balance': reserve_account,
            'mento_rate': mento_rate
    }

    def reset(self):
        self.__init__()
        print('buy_and_sell_manager reset!')


# Initialize buy_and_sell_manager
buy_and_sell_manager = BuyAndSellManager()
actor_manager = ActorManager()


# TODO: Improve this!
# Must be used at beginning of first policy of all buy_and_sell state_update_block
def reset_buy_and_sell_manager_if_new_parameter_subset(state_history):
    if len(state_history) == 1:
        buy_and_sell_manager.reset()


def reset_actor_manager_if_new_parameter_subset(state_history):
    if len(state_history) == 1:
        actor_manager.reset()


def p_random_exchange(params, substep, state_history, prev_state):

    # TODO: Check this earlier if possible / use decorator
    if not buy_and_sell_manager.buy_and_sell_feature_enabled(params):
        return buy_and_sell_manager.leave_all_state_variables_unchanged(
            prev_state=prev_state,
            policy_type='p_random_exchange'
        )

    # TODO: Find better solution
    reset_buy_and_sell_manager_if_new_parameter_subset(state_history)

    random_trade = buy_and_sell_manager.create_random_trade(
        params=params, prev_state=prev_state
    )

    state_variables_after_trade = buy_and_sell_manager.state_variables_state_after_trade(
        prev_state=prev_state,
        trade=random_trade
    )

    return state_variables_after_trade


def p_buy_and_sell_arb_actor(params, substep, state_history, prev_state):

    # TODO: Check this
    # if not params['actors_enabled']

    # TODO: Improve this
    # Only create one buy_and_sell_arb actor per parameter set
    if len(state_history) == 1:
        buy_and_sell_arb_actor_id = actor_manager.create_new_funded_actor(
            celo=params['arb_actor_init_celo_balance'],
            cusd=params['arb_actor_init_cusd_balance'],
            strategy_type='buy_and_sell_arb'
        )
        actor_manager.trigger_optimal_action(
            buy_and_sell_arb_actor_id
        )






    random_trade = buy_and_sell_manager.create_random_trade(
        params=params, prev_state=prev_state
    )

    state_variables_after_trade = buy_and_sell_manager.state_variables_state_after_trade(
        prev_state=prev_state,
        trade=random_trade
    )

    return state_variables_after_trade


def p_bucket_update(params, substep, state_history, prev_state):
    """
    Only update buckets every update_frequency_seconds
    """

    # TODO: Check this earlier if possible / use decorator
    if not buy_and_sell_manager.buy_and_sell_feature_enabled(params):
        return buy_and_sell_manager.leave_all_state_variables_unchanged(
            prev_state=prev_state,
            policy_type='p_bucket_update'
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
            policy_type='p_bucket_update'
        )
