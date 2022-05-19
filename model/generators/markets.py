"""
market price generator and related functions
"""

from enum import Enum
import logging
import numpy as np

from QuantLib import (TimeGrid, StochasticProcessArray,
                      UniformRandomGenerator, UniformRandomSequenceGenerator,
                      GaussianRandomSequenceGenerator, GaussianMultiPathGenerator)

from experiments import simulation_configuration
from model import constants
from model.utils.data_feed import data_feed
from model.utils.generator import Generator

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
        price_impact_model=PriceImpact.ROOT_QUANTITY,
        increments=None,
        seed=1,
        custom_impact_function=None,
    ):
        self.seed = seed
        self.price_impact_model = price_impact_model
        self.model = model
        self.increments = increments
        self.supply_changes = {asset.split('_')[0]: np.zeros(
            simulation_configuration.BLOCKS_PER_TIMESTEP
            * simulation_configuration.TIMESTEPS
            + 1) for asset in impacted_assets}
        self.data_folder = "../../data/"
        self.custom_impact_function = custom_impact_function

    @classmethod
    def from_parameters(cls, params):
        if params["model"] == MarketPriceModel.QUANTLIB:
            market_price_generator = cls(
                params["model"], params['impacted_assets']
            )
            if market_price_generator.price_impact_model == PriceImpact.CUSTOM:
                market_price_generator.custom_impact_function = params["custom_impact"]
            quant_lib_wrapper = QuantLibWrapper(
                params['processes'], params['correlation'])
            market_price_generator.increments = quant_lib_wrapper.correlated_returns()
        elif params["model"] == MarketPriceModel.PRICE_IMPACT:
            market_price_generator = cls(params["model"], params['impacted_assets'])
            if market_price_generator.price_impact_model == PriceImpact.CUSTOM:
                market_price_generator.custom_impact_function = params["custom_impact"]
        elif params["model"] == MarketPriceModel.HIST_SIM:
            market_price_generator = cls(params["model"], params['impacted_assets'])
            if market_price_generator.price_impact_model == PriceImpact.CUSTOM:
                market_price_generator.custom_impact_function = params["custom_impact"]
            # market_price_generator.load_historical_data(params["data_file"])
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
            # market_price_generator.load_historical_data(params["data_file"])
            sample_size = (
                simulation_configuration.BLOCKS_PER_TIMESTEP
                * simulation_configuration.TIMESTEPS
                + 1
            )
            market_price_generator.historical_returns(sample_size)
            logging.info("increments updated")
        return market_price_generator

    def market_price(self, state):
        """
        This method returns a market price
        """
        # TODO check that slicing with step is correct
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

        # elif self.model == MarketPriceModel.PRICE_IMPACT:
        #     # TODO  demand increment missing -> DemandGenerator
        #     market_prices = None
        #     # self.valuate_price_impact(state['supply'],
        #     #  #state['market_buckets'], #step-1)
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
        # elif mode == PriceImpact.CUSTOM:
        #    impact_function = self.custom_impact_function
        # elif mode == PriceImpact.CONSTANT_FIAT
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
        data, assets, length = (data_feed.data, data_feed.assets, data_feed.length)

        if self.model == MarketPriceModel.HIST_SIM:
            data = data[np.random.randint(low=0, high=length - 1, size=sample_size), :]
        increments = {}
        for index, asset in enumerate(assets):
            increments[asset] = data[:, index]
        self.increments = increments

        logging.info("Historic increments created")


class QuantLibWrapper():
    """
    This class wraps part of QuantLib to create increments
    """

    def __init__(self, processes, correlation,
                 _blocks_per_timestep=simulation_configuration.BLOCKS_PER_TIMESTEP,
                 _timesteps=simulation_configuration.TIMESTEPS, _number_of_paths=1):
        self.processes = processes
        self.correlation = correlation
        # as we use the log returns of each process initial value is irrelevant for processes
        # with independent multiplicative increments
        self.initial_value = 1
        self.number_of_paths_per_asset = 1

    def process_container(self,
                          blocks_per_timestep=simulation_configuration.BLOCKS_PER_TIMESTEP):
        """
        Creates an array of processes
        """
        timesteps_per_year = constants.blocks_per_year // blocks_per_timestep
        #     sample_size = timesteps * blocks_per_timestep + 1

        processes = [asset['process'](
            self.initial_value,
            asset['param_1'] / timesteps_per_year,
            asset['param_2'] / np.sqrt(timesteps_per_year))
            for ticker, asset in self.processes.items()]
        process_array = StochasticProcessArray(processes, self.correlation)
        return process_array

    def correlated_returns(self,
                           _blocks_per_timestep=simulation_configuration.BLOCKS_PER_TIMESTEP,
                           _timesteps=simulation_configuration.TIMESTEPS):
        log_returns = self.generate_correlated_paths()
        increments = {}
        for asset, path in zip(self.processes, log_returns):
            increments[asset] = path
        return increments

    # pylint: disable = too-many-locals
    def generate_correlated_paths(self,
                                  _blocks_per_timestep=simulation_configuration.BLOCKS_PER_TIMESTEP,
                                  timesteps=simulation_configuration.TIMESTEPS):
        """
        Generates paths
        """
        process = self.process_container()
        time_grid = TimeGrid(timesteps, timesteps)
        if isinstance(process, StochasticProcessArray):
            # time points are not really required for block step size but will if we change
            # to other time delta
            time_points = []
            for index, _time in enumerate(time_grid):
                time_points.append(time_grid[index])
            steps = (len(time_points) - 1) * process.size()
            sequence_generator = UniformRandomSequenceGenerator(
                steps, UniformRandomGenerator())
            gaussian_sequence_generator = GaussianRandomSequenceGenerator(
                sequence_generator)
            path_generator = GaussianMultiPathGenerator(
                process, time_points, gaussian_sequence_generator, False)
            paths = np.zeros(shape=(self.number_of_paths_per_asset,
                                    process.size(), len(time_grid)))

            for path_index in range(self.number_of_paths_per_asset):
                multi_path_generator = path_generator.next().value()
                for j in range(multi_path_generator.assetNumber()):
                    path = multi_path_generator[j]
                    paths[path_index, j, :] = np.array(
                        [path[k] for k in range(len(path))])

        log_returns = np.diff(np.log(paths[0]))

        return log_returns

    # def generate_uncorrelated_paths(self):
    #         sequence_generator = UniformRandomSequenceGenerator(
    #             len(time_grid), UniformRandomGenerator())
    #         gaussian_sequence_generator = GaussianRandomSequenceGenerator(
    #             sequence_generator)
    #         maturity = time_grid[len(time_grid) - 1]
    #         path_generator = GaussianPathGenerator(
    #             process, maturity, len(time_grid), gaussian_sequence_generator, False)
    #         paths = np.zeros(shape=(number_of_paths, len(time_grid)))
    #         for path_index in range(number_of_paths):
    #             path = path_generator.next().value()
    #             paths[path_index, :] = np.array(
    #                 [path[j] for j in range(len(time_grid))])

    #     log_returns = np.diff(np.log(paths[0]))
    #     # the current setup does only support simulation of processes with independent
    #     # increments or processes without if the value is not changed in other sub-steps
    #     increments = {}
    #     for asset, path in list(zip(self.processes, log_returns)):
    #         increments[asset] = path

    #     return increments

    # def switcher(self, params):
    #     if (np.array(params['correlation']) -
    #         np.diag(np.ones(len(params['correlation'])))
    #             == np.zeros(np.array(params['correlation']).shape)).all():
    #         process = self.process_container(params=params)
    #     else:
    #         process = None
    #     return process
