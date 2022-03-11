"""
# Market related policy and state update functions
"""
import logging
from enum import Enum
import numpy as np


# import dask.dataframe as dd
import pandas as pd
from experiments import simulation_configuration
from model import constants
from model.generators import Generator


class MarketPriceModel(Enum):
    GBM = "gbm"
    PRICE_IMPACT = "price_impact"
    HIST_SIM = "hist_sim"


class PriceImpact(Enum):
    CONSTANT_FIAT = "constant_fiat"
    CONSTANT_PRODUCT = "constant_product"
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
        drift,
        covariance,
        price_impact_model=PriceImpact.CONSTANT_PRODUCT,
        historical_data=None,
        increments=None,
        seed=1,
        custom_impact_function=None,
    ):
        self.seed = seed
        self.price_impact_model = price_impact_model
        self.model = model
        self.mc_parameter = {"drift": drift, "covariance": covariance}
        self.historical_data = historical_data
        self.increments = increments
        self.supply_changes = {
            "cusd": np.zeros(
                simulation_configuration.BLOCKS_PER_TIMESTEP
                * simulation_configuration.TIMESTEPS
                + 1
            ),
            "celo": np.zeros(
                simulation_configuration.BLOCKS_PER_TIMESTEP
                * simulation_configuration.TIMESTEPS
                + 1
            ),
        }
        self.data_folder = "../../data/"
        self.custom_impact_function = custom_impact_function

    @classmethod
    def from_parameters(cls, params):
        if params["model"] == MarketPriceModel.GBM:
            market_price_generator = cls(
                params["model"],
                params["drift_market_price"],
                params["covariance_market_price"],
            )
            if market_price_generator.price_impact_model == PriceImpact.CUSTOM:
                market_price_generator.custom_impact_function = params[
                    "custom_impact"
                ]
            market_price_generator.correlated_returns()
        elif params["model"] == MarketPriceModel.PRICE_IMPACT:
            market_price_generator = cls(params["model"], None, None)
            if market_price_generator.price_impact_model == PriceImpact.CUSTOM:
                market_price_generator.custom_impact_function = params[
                    "custom_impact"
                ]
        elif params["model"] == MarketPriceModel.HIST_SIM:
            market_price_generator = cls(params["model"], None, None)
            if market_price_generator.price_impact_model == PriceImpact.CUSTOM:
                market_price_generator.custom_impact_function = params[
                    "custom_impact"
                ]
            market_price_generator.load_historical_data(params["data_file"])
            sample_size = (
                simulation_configuration.BLOCKS_PER_TIMESTEP
                * simulation_configuration.TIMESTEPS
                + 1
            )
            market_price_generator.historical_returns(sample_size)
            logging.info("increments updated")
        return market_price_generator

    def load_historical_data(self, file_name):
        """
        Parser to read prices and turn them into log-returns"""
        # TODO parser

        if file_name[-3:] == "csv":
            historical_data = pd.read_csv(self.data_folder + file_name)
        elif file_name[-3:] == "prq":
            historical_data = pd.read_parquet(self.data_folder + file_name)
        self.historical_data = historical_data

    def market_price(self, state):
        """
        This method returns a market price
        """
        step = state["timestep"]
        if self.model == MarketPriceModel.GBM:
            market_prices = {
                "cusd_usd": (
                    state["market_price"]["cusd_usd"]
                    * self.increments["cusd_usd"][step - 1]
                ),
                "celo_usd": (
                    state["market_price"]["celo_usd"]
                    * self.increments["celo_usd"][step - 1]
                ),
            }

        elif self.model == MarketPriceModel.HIST_SIM:
            increment = self.increments.loc[step - 1]
            market_prices = {
                "cusd_usd": (state["market_price"]["cusd_usd"] * increment["cusd_usd"]),
                "celo_usd": (state["market_price"]["celo_usd"] * increment["celo_usd"]),
            }

        # elif self.model == MarketPriceModel.PRICE_IMPACT:
        #     # TODO  demand increment missing -> DemandGenerator
        #     market_prices = None
        #     # self.valuate_price_impact(state['supply'],
        #     #  #state['market_buckets'], #step-1)
        return market_prices

    def price_impact_function(self, mode):
        if mode == PriceImpact.CONSTANT_PRODUCT:
            impact_function = lambda asset_1, asset_2: asset_1 / asset_2
        elif mode == PriceImpact.CUSTOM:
            impact_function = self.custom_impact_function
        # elif mode == PriceImpact.CONSTANT_FIAT
        return impact_function

    def valuate_price_impact(
        self, floating_supply, pre_floating_supply, market_buckets, current_step
    ):
        """
        This functions evaluates price impact of supply changes
        """
        block_supply_change = {
            ccy: supply - pre_floating_supply[ccy]
            for ccy, supply in floating_supply.items()
        }
        quote_ccy = list(market_buckets.keys())[0]
        self.impact_delay(block_supply_change, current_step)
        effective_supply = {
            ccy: self.supply_changes[ccy][current_step] + pre_supply
            for ccy, pre_supply in pre_floating_supply.items()
        }

        return {
            f"{ccy}_{quote_ccy}": self.price_impact_function(self.price_impact_model)(
                supply, market_buckets[quote_ccy]
            )
            for ccy, supply in effective_supply.items()
        }

    def correlated_returns(
        self,
        blocks_per_timestep=simulation_configuration.BLOCKS_PER_TIMESTEP,
        timesteps=simulation_configuration.TIMESTEPS,
    ):
        """
        This function generates lognormal returns
        """
        # TODO use quantlib
        timesteps_per_year = constants.blocks_per_year // blocks_per_timestep
        sample_size = timesteps * blocks_per_timestep + 1
        drift = np.array(self.mc_parameter["drift"])
        cov = np.array(self.mc_parameter["covariance"]) / (timesteps_per_year)
        increments = np.exp(np.random.multivariate_normal(drift, cov, sample_size))
        self.increments = {"cusd_usd": increments[:, 0], "celo_usd": increments[:, 1]}

        # return increments

    def impact_delay(
        self, block_supply_change, current_step, impact_delay=ImpactDelay.INSTANT
    ):
        for ccy in block_supply_change:
            if impact_delay == ImpactDelay.INSTANT:
                self.supply_changes[ccy][current_step] += block_supply_change[ccy]

    def historical_returns(self, sample_size):
        """Creates a random sample from a set of historical log-returns"""
        # TODO move historical data handling into sperate class
        # TODO Consider different sampling options
        # TODO Random Seed
        nrows = len(self.historical_data)
        samples = self.historical_data.sample(frac=sample_size / nrows)
        # TODO does it make sense to free the memory?
        self.historical_data = [None]
        samples = samples.reset_index(drop=True)
        # samples_array = samples.to_dask_array(lengths = True)
        # TODO conversion to pandas frame is slow!!!
        self.increments = samples  # .compute()

        logging.info("Historic increments created")

    @property
    def cusd_usd_price(self):
        return self.cusd_usd_price

    @cusd_usd_price.setter
    def cusd_usd_price(self, value):
        self.cusd_usd_price = value

    def next_state(self, prev_state):
        pass


# class DemandGenerator:
#    def __init__(self):
#        self.demand_increment = None
