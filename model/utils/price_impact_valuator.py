"""
Provides Class for price impact valuation
"""
from typing import Callable, Dict, List
import numpy as np

from model.system_parameters import Parameters
from model.types.base import Fiat, ImpactDelayType, PriceImpact
from model.types.pair import Pair

PRICE_IMPACT_FUNCTION: Dict[PriceImpact, Callable] = {
    PriceImpact.ROOT_QUANTITY:
        lambda asset_quantity, variance_daily, average_daily_volume:
            -np.sign(asset_quantity)
            * np.sqrt(variance_daily * abs(asset_quantity) / average_daily_volume)
}


class PriceImpactValuator():
    """
    This class evaluates the price impact of trades with CEX / general off-chain market
    """

    impacted_assets: List[Pair]

    def __init__(self, impacted_assets: List[Pair], sample_size):
        self.impacted_assets = impacted_assets
        self.supply_changes = {
            pair.base: np.zeros(sample_size)
            for pair in impacted_assets
        }
        self.sample_size = sample_size
        self.price_impact_model = PriceImpact.ROOT_QUANTITY

    def price_impact(
        self,
        floating_supply,
        pre_floating_supply,
        current_step,
        market_prices,
        params: Parameters
    ):
        """
        This functions evaluates price impact of supply changes
        """
        block_supply_change = {
            ccy: supply - pre_floating_supply[ccy]
            for ccy, supply in floating_supply.items()
        }
        self.impact_delay(block_supply_change, current_step, params)

        impacted_prices = market_prices.copy()

        for pair in self.impacted_assets:
            if isinstance(pair.base, Fiat):
                raise Exception(f'Incorrect quoting convention for {pair}')
            variance_daily = params["variance_market_price"][pair] / 365
            average_daily_volume = params["average_daily_volume"][pair]
            impact_fn = PRICE_IMPACT_FUNCTION.get(self.price_impact_model)
            assert impact_fn is not None, f"{self.price_impact_model} does not have a function"
            price_impact = impact_fn(
                self.supply_changes[pair.base][current_step],
                variance_daily,
                average_daily_volume,
            )
            impacted_prices[pair] += price_impact
        return impacted_prices

    def impact_delay(
        self, block_supply_change, current_step, params: Parameters
    ):
        """
        This function distributes / delays supply changes across future timesteps
        """
        impact_delay = params['impact_delay']
        for ccy in block_supply_change:
            if impact_delay.model == ImpactDelayType.INSTANT:
                self.supply_changes[ccy][current_step] += block_supply_change[ccy]

            elif impact_delay.model == ImpactDelayType.NBLOCKS:
                delay = impact_delay.param_1
                for block in range(current_step, current_step +
                                   min(delay, self.sample_size % current_step)):
                    self.supply_changes[ccy][block] += (1 /
                                                        min(delay,
                                                            self.sample_size %
                                                            current_step) *
                                                        block_supply_change[ccy])
