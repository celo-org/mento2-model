"""
BuyAndSell Generator

BuyAndSell management implementing buy and sell trades
"""
import numpy as np
from model.constants import blocktime_seconds
from model.parts.utils.trade import Trade
from model.generators.accounts import AccountGenerator
from model.generators.generator import Generator
from model.generators.container import container


class BuyAndSellGenerator(Generator):
    """
    This class handles buy and sell trades with Mento
    """

    def __init__(self):
        self.total_celo_bought = 0
        self.total_celo_sold = 0
        self.total_cusd_bought = 0
        self.total_cusd_sold = 0

    @classmethod
    def from_parameters(cls, params) -> "BuyAndSellGenerator":

        return cls()

    @staticmethod
    def leave_all_state_variables_unchanged(prev_state, policy_type):
        if policy_type == 'p_random_exchange':
            return {
                'mento_buckets': prev_state['mento_buckets'],
                'floating_supply': prev_state['floating_supply'],
                'reserve_balance': prev_state['reserve_balance'],
                'mento_rate': prev_state['mento_rate']
            }
        return {'mento_buckets': prev_state['mento_buckets']}

    @staticmethod
    def buy_and_sell_feature_enabled(params):
        return params['feature_buy_and_sell_stables_enabled']

    @staticmethod
    def buckets_should_be_reset(params, prev_state):
        return (blocktime_seconds * prev_state['timestep']) % params[
            'bucket_update_frequency_seconds'] == 0

    @staticmethod
    @container.inject(AccountGenerator)
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
    def calculate_buy_amount_constant_product_amm(params, prev_state, sell_amount, sell_gold,
                                                  min_buy_amount=0):
        """
        amm calcs and logic
        """
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

    @staticmethod
    def create_random_trade(params, prev_state):
        """
        Trade are given from perspective of a trader, i.e. sell_gold=True
         means a trader sells CELO to the reserve
        """
        sell_fraction = BuyAndSellGenerator._get_random_sell_fraction(params)
        sell_gold = np.random.rand() > 0.5
        if sell_gold:
            sell_amount = sell_fraction * prev_state['floating_supply']['celo']
        else:
            sell_amount = sell_fraction * prev_state['floating_supply']['cusd']

        buy_amount = BuyAndSellGenerator.calculate_buy_amount_constant_product_amm(
            params=params,
            prev_state=prev_state,
            sell_amount=sell_amount,
            sell_gold=sell_gold
        )

        trade = BuyAndSellGenerator.create_trade(
            sell_gold=sell_gold,
            sell_amount=sell_amount,
            buy_amount=buy_amount
        )

        return trade

    @staticmethod
    def create_trade(sell_gold, sell_amount, buy_amount):
        """
        Trade are given from perspective of a trader, i.e. sell_gold=True
         means a trader sells CELO to the reserve
        """
        trade = Trade(
            sell_gold=sell_gold,
            sell_amount=sell_amount,
            buy_amount=buy_amount
        )
        return trade

    @staticmethod
    @container.inject(AccountGenerator)
    def state_variables_state_after_trade(prev_state, trade):
        """
        Trades and deltas are given from perspective of a trader, i.e. sell_gold=True means a trader
        has a negative delta_celo
        """

        # TODO: Update account balances using AccountGenerator!

        # Mento buckets are virtual so they do not count neither to
        # floating supply nor to the reserve balance
        mento_buckets = {
            'cusd': prev_state['mento_buckets']['cusd'] + trade.delta_mento_bucket_cusd,
            'celo': prev_state['mento_buckets']['celo'] + trade.delta_mento_bucket_celo
        }

        # If trader has positive delta, floating supply delta is positive
        # (trader balance is part of float)
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
