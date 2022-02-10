"""
# Market related policy and state update functions
"""
import logging
import random
import numpy as np

from enum import Enum
from pstats import Stats
import time

import dask
import dask.dataframe as dd
import experiments.simulation_configuration as simulation_configuration
from model import constants

from model.generators import Generator

from experiments.utils import rng_generator


class MarketPriceModel(Enum):
    GBM = 'gbm'
    PRICE_IMPACT = 'price_impact'
    HIST_SIM = 'hist_sim'


class PriceImpact(Enum):
    CONSTANT_FIAT = 'constant_fiat'
    CONSTANT_PRODUCT = 'constant_product'


class ImpactDelay(Enum):
    INSTANT = 'instant'


class MarketPriceGenerator(Generator):
    # TODO multi currency configurable
    # TODO in particular delay for Celo supply
    # TODO typing
    # TODO All seeds as params
    # TODO Comments

    def __init__(self, model, drift, covariance,
                 price_impact_model=PriceImpact.CONSTANT_PRODUCT,
                 historical_data=None, increments=[None], seed=1
                 ):
        self.seed = seed
        self.price_impact_model = price_impact_model
        self.model = model
        self.drift = drift
        self.covariance = covariance
        self.historical_data = historical_data
        self.increments = increments
        self.supply_changes = {'cusd': np.zeros(
            simulation_configuration.BLOCKS_PER_TIMESTEP * simulation_configuration.TIMESTEPS+1),
            'celo': np.zeros(
            simulation_configuration.BLOCKS_PER_TIMESTEP * simulation_configuration.TIMESTEPS+1)}
        self.data_folder = '../../data/'

    @classmethod
    def from_parameters(cls, parameters):
        if parameters['model'] == MarketPriceModel.GBM:
            print()
            market_price_generator = cls(parameters['model'],
                                         parameters['drift_market_price'],
                                         parameters['covariance_market_price'])
            market_price_generator.correlated_returns()
            return market_price_generator
        elif parameters['model'] == MarketPriceModel.PRICE_IMPACT:
            return cls(parameters['model'],
                       None,
                       None)
        elif parameters['model'] == MarketPriceModel.HIST_SIM:
            market_price_generator = cls(parameters['model'],
                                         None,
                                         None)
            market_price_generator.load_historical_data(parameters['data_file'])
            sample_size = simulation_configuration.BLOCKS_PER_TIMESTEP * \
                simulation_configuration.TIMESTEPS + 1
            market_price_generator.historical_returns(sample_size=sample_size, seed=1)
            logging.info('increments updated')
            return market_price_generator

    def load_historical_data(self, file_name):
        """
        Parser to read prices and turn them into log-returns"""
        # TODO parser

        #df = dd.read_csv(self.data_folder + file_name)
        df = dd.read_parquet(self.data_folder + file_name)
        self.historical_data = df

    def market_price(self, state):
        step = state['timestep']
        if self.model == MarketPriceModel.GBM:
            return {'cusd_usd': state['market_price']['cusd_usd'] * self.increments['cusd_usd'][step-1],
                    'celo_usd': state['market_price']['celo_usd'] * self.increments['celo_usd'][step-1]}

        elif self.model == MarketPriceModel.PRICE_IMPACT:
            # TODO  demand increment missing
            return self.valuate_price_impact(state['supply'], state['virtual_tanks'], step-1)
        elif self.model == MarketPriceModel.HIST_SIM:
            increment = self.increments.loc[step-1]
            return {'cusd_usd': state['market_price']['cusd_usd'] * increment['cusd_usd'],
                    'celo_usd': state['market_price']['celo_usd'] * increment['celo_usd']}

    def price_impact_function(self, mode):
        return lambda asset_1, asset_2: asset_1 / asset_2
        # elif mode == PriceImpact.CONSTANT_FIAT
        #    return lambda

    def valuate_price_impact(self, floating_supply, pre_floating_supply, virtual_tanks, current_step):
        block_supply_change = {
            ccy: supply - pre_floating_supply[ccy] for ccy, supply in floating_supply.items()}
        quote_ccy = list(virtual_tanks.keys())[0]
        self.impact_delay(block_supply_change, current_step)
        effective_supply = {ccy: self.supply_changes[ccy][current_step] +
                            pre_supply for ccy, pre_supply in pre_floating_supply.items()}

        return {f'{ccy}_{quote_ccy}':
                self.price_impact_function(self.price_impact_model)(
                    supply, virtual_tanks[quote_ccy])
                for ccy, supply in effective_supply.items()}

    def correlated_returns(
            self, dt=simulation_configuration.BLOCKS_PER_TIMESTEP,
            timesteps=simulation_configuration.TIMESTEPS):
        # TODO use quantlib
        timesteps_per_year = constants.blocks_per_year // dt
        sample_size = timesteps * dt + 1
        mu = np.array(self.drift)
        cov = np.array(self.covariance) / (timesteps_per_year)
        increments = np.exp(np.random.multivariate_normal(mu, cov, sample_size))
        self.increments = {'cusd_usd': increments[:, 0], 'celo_usd': increments[:, 1]}

        # return increments

    # TODO add delay that creates time lag between Mento trades and price impact

    def impact_delay(self, block_supply_change, current_step,
                     impact_delay=ImpactDelay.INSTANT,
                     dt=simulation_configuration.BLOCKS_PER_TIMESTEP,
                     timesteps=simulation_configuration.TIMESTEPS):
        for ccy in block_supply_change:
            if impact_delay == ImpactDelay.INSTANT:
                unit_array = np.zeros(timesteps * dt + 1)
                unit_array[current_step] = 1
                def delay_envelope(x): return x * unit_array
                self.supply_changes[ccy] += delay_envelope(block_supply_change[ccy])

    def historical_returns(self, sample_size, seed):
        """Creates a random sample from a set of historical log-returns
        """
        # TODO move historical data handling into sperate class
        # TODO Consider different sampling options
        sample_size = simulation_configuration.BLOCKS_PER_TIMESTEP * \
            simulation_configuration.TIMESTEPS
        # TODO Hardcoded data length
        samples = self.historical_data.sample(frac=(
            simulation_configuration.BLOCKS_PER_TIMESTEP * simulation_configuration.TIMESTEPS + 1)/6307200)
        #self.historical_data = [None]
        samples = samples.reset_index(drop=True)
        #samples_array = samples.to_dask_array(lengths = True)
        # TODO conversion to pandas frame is slow!!!
        self.increments = samples.compute()

        logging.info(f'Historic increments created')

    @property
    def cusd_usd_price(self):
        return self.cusd_usd_price

    @cusd_usd_price.setter
    def cusd_usd_price(self, value):
        self.cusd_usd_price = value

    def next_state(self, prev_state):
        pass


class DemandGenerator():
    def __init__(self):
        self.demand_increment = None
