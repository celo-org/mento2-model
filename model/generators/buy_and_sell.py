"""
BuyAndSell Generator

BuyAndSell management implementing buy and sell trades
"""
import numpy as np
from model.constants import blocktime_seconds
from model.generators.generator import Generator


class BuyAndSellGenerator(Generator):
    """
    This class handles buy and sell trades with Mento
    """

    def __init__(self,spread):
        self.total_celo_bought = 0
        self.total_celo_sold = 0
        self.total_cusd_bought = 0
        self.total_cusd_sold = 0
        self.spread = spread

    @classmethod
    def from_parameters(cls, params) -> "BuyAndSellGenerator":
        # TODO what to do here?
        return cls(spread=params['spread'])

    @staticmethod
    def buckets_should_be_reset(params, prev_state):
        update_required = ((blocktime_seconds * prev_state['timestep']) % params[
              'bucket_update_frequency_seconds'] == 0)
        return update_required

    # @staticmethod
    # def reset_buckets(params, prev_state, account_generator):
    #     """
    #     mento bucket update
    #     """
    #     celo_bucket = params['reserve_fraction'] * prev_state['reserve_balance']['celo']
    #     # change reserve account balance
    #     delta_celo = prev_state['reserve_balance']['celo'] - celo_bucket
    #     account_generator\
    #         .change_account_balance(account_id=account_generator,
    #                                 delta_celo=delta_celo,
    #                                 delta_cusd=0)
    #     cusd_bucket = prev_state['celo_usd_price'] * celo_bucket
    #     mento_buckets = {
    #         'cusd': cusd_bucket,
    #         'celo': celo_bucket
    #     }
    #     return {
    #         'mento_buckets': mento_buckets
    #     }
    @staticmethod
    def bucket_update(params, prev_state):
        celo_bucket = params['reserve_fraction'] * prev_state['reserve_account']['celo']
        cusd_bucket = prev_state['mento_rate'] * celo_bucket
        mento_buckets = {
            'cusd': cusd_bucket,
            'celo': celo_bucket
        }
        return {'mento_buckets': mento_buckets}

    # @staticmethod
    # def _get_random_sell_fraction(params):
    #     return np.random.rand() * params['max_sell_fraction_of_float']

    # @staticmethod
    # def create_random_trade(params, prev_state):
    #     """
    #     Trade are given from perspective of a trader, i.e. sell_gold=True
    #      means a trader sells CELO to the reserve
    #     """
    #     sell_fraction = BuyAndSellGenerator._get_random_sell_fraction(params)
    #     sell_gold = np.random.rand() > 0.5
    #     if sell_gold:
    #         sell_amount = sell_fraction * prev_state['floating_supply']['celo']
    #     else:
    #         sell_amount = sell_fraction * prev_state['floating_supply']['cusd']

    #     buy_amount = BuyAndSellGenerator.calculate_buy_amount_constant_product_amm(
    #         params=params,
    #         prev_state=prev_state,
    #         sell_amount=sell_amount,
    #         sell_gold=sell_gold
    #     )

    #     trade = Trade(
    #         sell_gold=sell_gold,
    #         sell_amount=sell_amount,
    #         buy_amount=buy_amount
    #     )
    #     return trade

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
    def state_after_trade(prev_state, trade, account_generator):
        """
        Trades and deltas are given from perspective of a trader, i.e. sell_gold=True means a trader
        has a negative delta_celo
        """

        # Mento buckets are virtual so they do not count neither to
        # floating supply nor to the reserve balance
        mento_buckets = {
            'cusd': prev_state['mento_buckets']['cusd'] + trade.delta_mento_bucket_cusd,
            'celo': prev_state['mento_buckets']['celo'] + trade.delta_mento_bucket_celo
        }

        # Update trader
        account_generator\
            .change_account_balance(account_id=account_generator.get_account(1)['account_id'],
                                    delta_celo=trade.delta_trader_celo,
                                    delta_cusd=trade.delta_trader_cusd)

        # Update reserve
        account_generator\
            .change_account_balance(account_id=account_generator.get_account(0)['account_id'],
                                    delta_celo=trade.delta_reserve_celo,
                                    delta_cusd=0.0)

        # New realized mento rate
        mento_rate = mento_buckets['cusd'] / mento_buckets['celo']

        return {
            'mento_buckets': mento_buckets,
            'mento_rate': mento_rate
        }

    def get_buy_amount(self, sell_amount, sell_gold, prev_state,  min_buy_amount=0):
        """
        Making pylint happy
        """
        reduced_sell_amount = sell_amount * (1 - self.spread)

        if sell_gold:
            buy_token_bucket = prev_state["mento_buckets"]["cusd"]
            sell_token_bucket = prev_state["mento_buckets"]["celo"]
        else:
            buy_token_bucket = prev_state["mento_buckets"]["celo"]
            sell_token_bucket = prev_state["mento_buckets"]["cusd"]

        numerator = sell_amount * (1 - self.spread) * buy_token_bucket
        denominator = sell_token_bucket + reduced_sell_amount
        buy_amount = numerator / denominator

        if buy_amount < min_buy_amount:
            buy_amount = np.nan

        return buy_amount

    def exchange(self, sell_amount, sell_gold, _substep, _state_history, prev_state):
        """
        Making pylint happy
        """
        if sell_gold:
            sell_amount = sell_amount / prev_state["mento_rate"]

        buy_amount = self.get_buy_amount(sell_amount, sell_gold, prev_state )

        if sell_gold:
            delta_cusd = -buy_amount
            delta_celo = sell_amount
        else:
            delta_cusd = sell_amount
            delta_celo = -buy_amount

        mento_buckets = {
            "cusd": prev_state["mento_buckets"]["cusd"] + delta_cusd,
            "celo": prev_state["mento_buckets"]["celo"] + delta_celo,
        }

        floating_supply = {
            "cusd": prev_state["floating_supply"]["cusd"] - delta_cusd,
            "celo": prev_state["floating_supply"]["celo"] - delta_celo,
        }

        reserve_account = {"celo": prev_state["reserve_account"]["celo"] + delta_celo}

        mento_rate = mento_buckets["cusd"] / mento_buckets["celo"]

        # market_price_generator = params['generators'].get(MarketPriceGenerator)
        # market_price = {'cusd_usd': market_price_generator.valuate(
        #    floating_supply['cusd'], virtual_tanks['usd'])}

        return (
            {
                "mento_buckets": mento_buckets,
                "floating_supply": floating_supply,
                "reserve_account": reserve_account,
                "mento_rate": mento_rate,
            },
            {"cusd": delta_cusd, "celo": delta_celo},
        )
