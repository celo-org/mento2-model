"""
market price generator and related functions
"""

import logging
import numpy as np

from experiments.simulation_configuration import TOTAL_BLOCKS
from model.system_parameters import Parameters

from model.types.base import MarketPriceModel
from model.utils.data_feed import DATA_FOLDER, DataFeed
from model.utils.generator import Generator
from model.utils.price_impact_valuator import PriceImpactValuator
from model.utils.quantlib_wrapper import QuantLibWrapper
from model.utils.rng_provider import rngp

# raise numpy warnings as errors
np.seterr(all='raise')


class MarketPriceGenerator(Generator):
    """
    This class is providing a market environment
    """

    price_impact_valuator: PriceImpactValuator

    # TODO multi currency configurable
    # TODO in particular delay for Celo supply
    # TODO typing
    # TODO Comments

    def __init__(
        self,
        model,
        impacted_assets,
        increments=None,
    ):
        self.model = model
        self.increments = increments
        self.price_impact_valuator = PriceImpactValuator(
            impacted_assets, TOTAL_BLOCKS)
        self.rng = rngp.get_rng("MarketPriceGenerator")

    @classmethod
    def from_parameters(cls, params: Parameters, _initial_state, _container):
        model = params["market_price_model"]
        if model == MarketPriceModel.QUANTLIB:
            market_price_generator = cls(
                model,
                params['impacted_assets']
            )
            quant_lib_wrapper = QuantLibWrapper(
                params['market_price_processes'],
                params['market_price_correlation_matrix'],
                TOTAL_BLOCKS
            )
            market_price_generator.increments = quant_lib_wrapper.correlated_returns()
        elif model == MarketPriceModel.PRICE_IMPACT:
            market_price_generator = cls(model, params['impacted_assets'])
        elif model == MarketPriceModel.HIST_SIM:
            market_price_generator = cls(model, params['impacted_assets'])
            market_price_generator.historical_returns()
            logging.info("increments updated")
        elif model == MarketPriceModel.SCENARIO:
            market_price_generator = cls(model, params['impacted_assets'])
            market_price_generator.historical_returns()
            logging.info("increments updated")
        return market_price_generator

    def market_price(self, state):
        """
        This method returns a market price
        """
        step = state["timestep"]
        market_prices = {}
        for asset in state["market_price"]:
            increments = self.increments.get(asset)
            if increments is None:
                scale_factor = 1
            else:
                scale_factor = np.exp(increments[step])
            market_prices[asset] = state["market_price"][asset] * scale_factor
        return market_prices

    def valuate_price_impact(
        self,
        floating_supply,
        pre_floating_supply,
        current_step,
        market_prices,
        params
    ):
        return self.price_impact_valuator.price_impact(floating_supply,
                                                       pre_floating_supply,
                                                       current_step,
                                                       market_prices,
                                                       params)

    def historical_returns(self):
        """Passes a historic scenario or creates a random sample from a set of
        historical log-returns"""
        # TODO Consider different sampling options
        # TODO Random Seed
        data_feed = DataFeed(data_folder=DATA_FOLDER)
        data = data_feed.data.copy()
        if self.model == MarketPriceModel.HIST_SIM:
            random_index_array = np.random.randint(low=0,
                                                   high=data_feed.length - 1,
                                                   size=TOTAL_BLOCKS)
            data = data_feed.data[random_index_array, :]
        increments = {}
        for index, asset in enumerate(data_feed.assets):
            increments[asset] = data[:, index]
        self.increments = increments
        logging.info("Historic increments created")
