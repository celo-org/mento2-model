"""
Mento generator

Handles one or more mento instances
"""

from typing import Any, Dict, Set
import numpy as np

from model.constants import blocktime_seconds
from model.entities.balance import Balance
from model.types.base import MentoBuckets, MentoExchange, Stable
from model.types.pair import Pair
from model.types.configs import MentoExchangeConfig
from model.utils.generator import Generator, state_update_blocks
from model.utils import update_from_signal

# raise numpy warnings as errors
np.seterr(all='raise')


class MentoExchangeGenerator(Generator):
    """
    The MentoExchangeGenerator emulates Mento AMMs that
    function as cross-product automated market maker between
    a virtual stable bucket and a reserve currency bucket.
    In v1 that's one of cUSD, cEUR and cREAL with CELO as
    the reserve currency.
    But the generator permits modeling AMMs backed by
    any reserves on other chains as well for example (cUSD, ETH).
    """
    configs: Dict[MentoExchange, MentoExchangeConfig]
    active_exchanges: Set[MentoExchange]

    def __init__(self, configs: Dict[Stable, MentoExchangeConfig], active_exchanges: Set[Stable]):
        self.configs = configs
        self.active_exchanges = active_exchanges

    @classmethod
    def from_parameters(cls, params, _initial_state, _container):
        return cls(
            params['mento_exchanges_config'],
            set(params['mento_exchanges_active'])
        )

    @state_update_blocks('bucket_update')
    def bucket_update(self):
        return [{
            'description': """
                Updates blocks only when update bucket_update_frequency_seconds has passed since last update.
            """,
            'policies': {
                'bucket_update': self.get_bucket_update_policy()
            },
            'variables': {
                'mento_buckets': update_from_signal('mento_buckets')
            }
        }]

    def get_bucket_update_policy(self):
        """
        Policy function which updates AMM buckets
        """
        def p_bucket_update(
            _params,
            _substep,
            _state_history,
            prev_state,
        ):
            mento_buckets = {
                exchange: self.get_next_buckets(prev_state, exchange)
                for exchange in self.active_exchanges
            }

            return {
                'mento_buckets': mento_buckets
            }
        return p_bucket_update

    def get_next_buckets(self, prev_state, exchange):
        """
        Get the next bucket sizes for a give exchange
        """
        update_required = self.buckets_should_be_reset(exchange, prev_state)
        if update_required:
            return self.recalculate_buckets(exchange, prev_state)
        return prev_state['mento_buckets'][exchange]

    def buckets_should_be_reset(self, exchange: MentoExchange, prev_state) -> bool:
        """
        Returns true if the buckets for a particular exchange have to be reset
        """
        bucket_update_frequency = self.configs[exchange].bucket_update_frequency_second
        update_required = (
            (blocktime_seconds * prev_state['timestep']) % bucket_update_frequency == 0
        ) or (prev_state['timestep'] == 1)
        return update_required

    def recalculate_buckets(self, exchange: MentoExchange, prev_state):
        """
        Recalculates the bucket sizes for a given exchange
        """
        config = self.configs[exchange]
        reserve_asset_bucket = (
            config.reserve_fraction
            * prev_state['reserve_balance'].get(config.reserve_asset)
        )
        stable_bucket = (
            prev_state['oracle_rate'].get(
                Pair(config.reserve_asset, config.reference_fiat))
            * reserve_asset_bucket
        )
        return MentoBuckets(stable=stable_bucket, reserve_asset=reserve_asset_bucket)

    def get_buy_amount(
            self,
            exchange: MentoExchange,
            sell_amount: float,
            sell_reserve_asset: bool,
            prev_state: Any,
            min_buy_amount: float = 0):
        """
        Calculates the amount of currency (either stable or reserve_asset)
        can be bought based on the buckets and spread.
        """
        spread = self.configs[exchange].spread
        reduced_sell_amount = sell_amount * (1 - spread)

        if sell_reserve_asset:
            buy_token_bucket = prev_state["mento_buckets"][exchange]['stable']
            sell_token_bucket = prev_state["mento_buckets"][exchange]['reserve_asset']
        else:
            buy_token_bucket = prev_state["mento_buckets"][exchange]['reserve_asset']
            sell_token_bucket = prev_state["mento_buckets"][exchange]['stable']

        numerator = sell_amount * (1 - spread) * buy_token_bucket
        denominator = sell_token_bucket + reduced_sell_amount
        buy_amount = numerator / denominator

        if buy_amount < min_buy_amount:
            buy_amount = np.nan

        return buy_amount

    def exchange(self, exchange: MentoExchange, sell_amount, sell_reserve_asset, prev_state):
        """
        Update the simulation state with a trade between the reserve currency and stable
        """
        config = self.configs.get(exchange)
        assert config is not None

        buy_amount = self.get_buy_amount(
            exchange, sell_amount, sell_reserve_asset, prev_state)

        if sell_reserve_asset:
            delta_stable = -buy_amount
            delta_reserve_asset = sell_amount
        else:
            delta_stable = sell_amount
            delta_reserve_asset = -buy_amount

        prev_bucket = prev_state["mento_buckets"][exchange]
        next_bucket = MentoBuckets(
            stable=prev_bucket['stable'] + delta_stable,
            reserve_asset=prev_bucket['reserve_asset'] + delta_reserve_asset
        )

        delta = Balance({
            config.reserve_asset: -1 * delta_reserve_asset,
            config.stable: -1 * delta_stable
        })

        return (next_bucket, delta)
