"""
Provides Class for price impact valuation
"""
import numpy as np

from experiments import simulation_configuration
from model.types import ImpactDelay, PriceImpact


class PriceImpactValuator():
    """
    This class evaluates the price impact of trades with CEX / general off-chain market
    """

    def __init__(self, impacted_assets, sample_size):
        self.supply_changes = {asset.split('_')[0]: np.zeros(
            simulation_configuration.BLOCKS_PER_TIMESTEP
            * simulation_configuration.TIMESTEPS
            + 1) for asset in impacted_assets}
        self.sample_size = sample_size
        self.price_impact_model = PriceImpact.ROOT_QUANTITY

    def price_impact(
        self,
        floating_supply,
        pre_floating_supply,
        current_step,
        market_prices,
        params
    ):
        """
        This functions evaluates price impact of supply changes
        """
        block_supply_change = {
            ccy: supply - pre_floating_supply[ccy]
            for ccy, supply in floating_supply.items()
        }
        self.impact_delay(block_supply_change, current_step, params)

        price_impact = {}
        prices = {}

        for asset in params['impacted_assets']:
            asset_1, _ = asset.split('_')
            if asset_1 == 'usd':
                raise Exception(f'Incorrect quoting convention for {asset}')
            variance_daily = params["variance_market_price"][asset] / 365
            average_daily_volume = params["average_daily_volume"][asset]
            price_impact[asset] = self.price_impact_function(self.price_impact_model)(
                self.supply_changes[asset_1][current_step],
                variance_daily,
                average_daily_volume,
            )
            prices[asset] = market_prices[asset] + price_impact[asset]

        return prices

    def impact_delay(
        self, block_supply_change, current_step, params
    ):
        """
        This function distributes / delays supply changes across future timesteps
        """
        impact_delay = params['impact_delay']
        for ccy in block_supply_change:
            if impact_delay['model'] == ImpactDelay.INSTANT:
                self.supply_changes[ccy][current_step] += block_supply_change[ccy]

            elif impact_delay['model'] == ImpactDelay.NBLOCKS:
                delay = impact_delay['param_1']
                for block in range(current_step, current_step +
                                   min(delay, self.sample_size % current_step)):
                    self.supply_changes[ccy][block] += (1 /
                                                        min(delay,
                                                            self.sample_size %
                                                            current_step) *
                                                        block_supply_change[ccy])

    # pylint: disable=no-self-use
    def price_impact_function(self, mode):
        """
        calculates the price impact of a trade
        """
        if mode == PriceImpact.ROOT_QUANTITY:
            impact_function = (
                lambda asset_quantity, variance_daily, average_daily_volume: -np.sign(
                    asset_quantity
                )
                * np.sqrt(variance_daily * abs(asset_quantity) / average_daily_volume)
            )

        return impact_function
