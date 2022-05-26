"""
market price generator and related functions
"""

import logging
import numpy as np


from experiments import simulation_configuration
from model.types import MarketPriceModel
from model.utils.data_feed import DATA_FILE_NAME, DATA_FOLDER, DataFeed
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

    # TODO multi currency configurable
    # TODO in particular delay for Celo supply
    # TODO typing
    # TODO All seeds as params
    # TODO unified seed generation
    # TODO Comments

    def __init__(
        self,
        model,
        impacted_assets,
        increments=None,
        seed=1,
        custom_impact_function=None,
    ):
        self.seed = seed
        self.model = model
        self.increments = increments
        self.sample_size = (simulation_configuration.BLOCKS_PER_TIMESTEP
                            * simulation_configuration.TIMESTEPS
                            + 1
                            )
        self.price_impact_valuator: PriceImpactValuator = PriceImpactValuator(
            impacted_assets, self.sample_size)
        self.data_folder = "../../data/"
        self.custom_impact_function = custom_impact_function
        self.rng = rngp.get_rng("MarketPriceGenerator")

    @classmethod
    def from_parameters(cls, params, _initial_state):
        if params["model"] == MarketPriceModel.QUANTLIB:
            market_price_generator = cls(
                params["model"], params['impacted_assets']
            )
            quant_lib_wrapper = QuantLibWrapper(
                params['processes'], params['correlation'], market_price_generator.sample_size)
            market_price_generator.increments = quant_lib_wrapper.correlated_returns()
        elif params["model"] == MarketPriceModel.PRICE_IMPACT:
            market_price_generator = cls(params["model"], params['impacted_assets'])
        elif params["model"] == MarketPriceModel.HIST_SIM:
            market_price_generator = cls(params["model"], params['impacted_assets'])
            market_price_generator.historical_returns()
            logging.info("increments updated")
        elif params["model"] == MarketPriceModel.SCENARIO:
            market_price_generator = cls(params["model"], params['impacted_assets'])
            market_price_generator.historical_returns()
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
        data_feed = DataFeed(data_folder=DATA_FOLDER, data_file_name=DATA_FILE_NAME)
        data = data_feed.historical_data
        if self.sample_size > (data_feed.length+1):
            raise RuntimeError(
                "Simulation time longer than historical return time series, "
                "`SCENARIO`based market price generation not possible"
            )
        if self.model == MarketPriceModel.HIST_SIM:
            random_index_array = np.random.randint(low=0,
                                                   high=data_feed.length - 1,
                                                   size=self.sample_size)
            data = data_feed.historical_data[random_index_array, :]
        increments = {}
        for index, asset in enumerate(data_feed.assets):
            increments[asset] = data[:, index]
        self.increments = increments

        logging.info("Historic increments created")
