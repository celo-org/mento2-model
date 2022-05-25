"""
market price generator and related functions
"""

from copy import deepcopy
from enum import Enum
import logging
from typing import List, Tuple
import numpy as np

from experiments import simulation_configuration

from model.types import Currency, Fiat
from model.utils.data_feed import DATA_FILE_NAME, DATA_FOLDER, DataFeed
from model.utils.generator import Generator
from model.utils.quantlib_wrapper import QuantLibWrapper
from model.utils.rng_provider import rngp

# raise numpy warnings as errors
np.seterr(all='raise')

class MarketPriceModel(Enum):
    QUANTLIB = "quantlib"
    PRICE_IMPACT = "price_impact"
    HIST_SIM = "hist_sim"
    SCENARIO = "scenario"


class PriceImpact(Enum):
    CONSTANT_FIAT = "constant_fiat"
    CONSTANT_PRODUCT = "constant_product"
    ROOT_QUANTITY = "root_quantity"
    CUSTOM = "custom"


class ImpactDelay(Enum):
    INSTANT = "instant"


class MarketPriceGenerator(Generator):
    """
    This class is providing a market environment
    """

    impacted_assets: List[Tuple[Currency, Fiat]]

    # TODO multi currency configurable
    # TODO in particular delay for Celo supply
    # TODO typing
    # TODO Comments
    def __init__(
        self,
        model,
        impacted_assets,
        price_impact_model=PriceImpact.ROOT_QUANTITY,
        increments=None,
        custom_impact_function=None,
    ):
        self.price_impact_model = price_impact_model
        self.model = model
        self.increments = increments
        self.supply_changes = {base: np.zeros(
            simulation_configuration.BLOCKS_PER_TIMESTEP
            * simulation_configuration.TIMESTEPS
            + 1) for (base, quote) in impacted_assets}
        self.impacted_assets = impacted_assets
        self.data_folder = "../../data/"
        self.custom_impact_function = custom_impact_function
        self.rng = rngp.get_rng("MarketPriceGenerator")

    @classmethod
    def from_parameters(cls, params, _initial_state):
        if params["model"] == MarketPriceModel.QUANTLIB:
            market_price_generator = cls(
                params["model"], params['impacted_assets']
            )
            if market_price_generator.price_impact_model == PriceImpact.CUSTOM:
                market_price_generator.custom_impact_function = params["custom_impact"]
            quant_lib_wrapper = QuantLibWrapper(
                params['market_price_processes'],
                params['market_price_correlation_matrix'],
            )
            market_price_generator.increments = quant_lib_wrapper.correlated_returns()
        elif params["model"] == MarketPriceModel.PRICE_IMPACT:
            market_price_generator = cls(params["model"], params['impacted_assets'])
            if market_price_generator.price_impact_model == PriceImpact.CUSTOM:
                market_price_generator.custom_impact_function = params["custom_impact"]
        elif params["model"] == MarketPriceModel.HIST_SIM:
            market_price_generator = cls(params["model"], params['impacted_assets'])
            if market_price_generator.price_impact_model == PriceImpact.CUSTOM:
                market_price_generator.custom_impact_function = params["custom_impact"]
            sample_size = (
                simulation_configuration.BLOCKS_PER_TIMESTEP
                * simulation_configuration.TIMESTEPS
                + 1
            )
            market_price_generator.historical_returns(sample_size)
            logging.info("increments updated")
        elif params["model"] == MarketPriceModel.SCENARIO:
            market_price_generator = cls(params["model"], params['impacted_assets'])
            if market_price_generator.price_impact_model == PriceImpact.CUSTOM:
                market_price_generator.custom_impact_function = params["custom_impact"]
            sample_size = (
                simulation_configuration.BLOCKS_PER_TIMESTEP
                * simulation_configuration.TIMESTEPS
                + 1
            )
            market_price_generator.historical_returns(sample_size)
            if sample_size > (market_price_generator.increments["cusd_usd"].shape[0]+1):
                raise RuntimeError(
                    "Simulation time longer than historical return time series, "
                    "`SCENARIO`based market price generation not possible"
                )
            logging.info("increments updated")
        return market_price_generator

    def market_price(self, state):
        """
        This method returns a market price
        """
        step = state["timestep"]
        market_prices = {}
        if self.model == MarketPriceModel.QUANTLIB:
            for asset in state["market_price"]:
                market_prices[asset] = (state["market_price"][asset]
                                        * np.exp(self.increments[asset][step - 1]))

        elif self.model == MarketPriceModel.HIST_SIM:
            for asset in state["market_price"]:
                market_prices[asset] = (state["market_price"][asset]
                                        * np.exp(self.increments[asset][step]))

        elif self.model == MarketPriceModel.SCENARIO:
            for asset in state["market_price"]:
                market_prices[asset] = (state["market_price"][asset]
                                        * np.exp(self.increments[asset][step]))

        return market_prices

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

    def valuate_price_impact(
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
        self.impact_delay(block_supply_change, current_step)

        impacted_prices = deepcopy(market_prices)
        for (base, quote) in self.impacted_assets:
            variance_daily = params["variance_market_price"][base][quote] / 365
            average_daily_volume = params["average_daily_volume"][base][quote]
            price_impact = self.price_impact_function(self.price_impact_model)(
                self.supply_changes[base][current_step],
                variance_daily,
                average_daily_volume,
            )
            impacted_prices[base][quote] += price_impact

        return impacted_prices

    def impact_delay(
        self, block_supply_change, current_step, impact_delay=ImpactDelay.INSTANT
    ):
        for ccy in block_supply_change:
            if impact_delay == ImpactDelay.INSTANT:
                self.supply_changes[ccy][current_step] += block_supply_change[ccy]

    def historical_returns(self, sample_size):
        """Passes a historic scenario or creates a random sample from a set of
        historical log-returns"""
        # TODO Consider different sampling options
        # TODO Random Seed
        data_feed = DataFeed(data_folder=DATA_FOLDER, data_file_name=DATA_FILE_NAME)
        data = data_feed.historical_data
        if self.model == MarketPriceModel.HIST_SIM:
            random_index_array = np.random.randint(low=0,
                                                   high=data_feed.length - 1,
                                                   size=sample_size)
            data = data_feed.historical_data[random_index_array, :]
        increments = {}
        for index, asset in enumerate(data_feed.assets):
            increments[asset] = data[:, index]
        self.increments = increments

        logging.info("Historic increments created")
