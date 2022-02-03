"""
# Market related policy and state update functions
"""
import random
import numpy as np

from enum import Enum
from opcode import stack_effect
from pstats import Stats
from stochastic import processes
from statsmodels.distributions.empirical_distribution import ECDF

import dask.dataframe as dd
import experiments.simulation_configuration as simulation_configuration

from model.generators import Generator
from model.constants import blocktime_seconds

from data import historical_values
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
    # Todo multi currency
    # Todo in particular delay for Celo supply
    # Todo typing
    # Todo All seeds as params
    # Todo check thhat not 'entire' object bis saved in state history

    def __init__(self, model, drift, volatility,
                 price_impact_model=PriceImpact.CONSTANT_PRODUCT,
                 historical_data=[None], increments=[None], seed=1
                 ):
        self.seed = seed
        self.price_impact_model = price_impact_model
        self.model = model
        self.drift = drift
        self.volatility = volatility
        self.historical_data = historical_data
        self.increments = increments
        self.supply_changes = np.zeros(
            simulation_configuration.DELTA_TIME * simulation_configuration.TIMESTEPS)
        # todo replace step by corresponding simulation counter
        self.step = 0

    @classmethod
    def from_parameters(cls, parameters):
        if parameters['model'] == MarketPriceModel.GBM:
            print()
            market_price_generator = cls(parameters['model'],
                                         parameters['drift_market_price'],
                                         parameters['volatility_market_price'])
            market_price_generator.generate_gbm_increments()
            return market_price_generator
        elif parameters['model'] == MarketPriceModel.PRICE_IMPACT:
            return cls(parameters['model'],
                       None,
                       None)
        elif parameters['model'] == MarketPriceModel.HIST_SIM:
            market_price_generator = cls(None,
                                         None,
                                         None)
            market_price_generator.load_historical_data(parameters['data_file'])
            return market_price_generator


    def load_historical_data(self, file_name):
        """
        Parser to read prices and turn them into log-returns"""
        # TODO parser
        df = dd.read_csv(file_name)
        self.historical_data = list(df['log_returns'])

    def observe_market_states(self, state):
        """
        !!! probably not needed!!!
        """
        return {'virtual_tank': state['virtual_tanks']['usd'],
                'supply': state['floating_supply']['cusd'],
                'market_price': state['market_price']['cusd_usd']}

    def market_price(self, state):
        self.step += 1
        if self.model == MarketPriceModel.GBM:
            return state['market_price']['cusd_usd'] * self.increments[self.step-1]
        elif self.model == MarketPriceModel.PRICE_IMPACT:
            return self.valuate_price_impact(state['supply'], state['virtual_tank'])
        elif self.model == MarketPriceModel.HIST_SIM:
            return state['market_price']['cusd_usd'] * self.increments[self.step-1]

    def price_impact_function(self, mode):
        return lambda asset_1, asset_2: asset_1 / asset_2
        # elif mode == PriceImpact.CONSTANT_FIAT
        #    return lambda

    def valuate_price_impact(self, supply, virtual_tank):
        delayed_supply = self.impact_delay(supply)
        return self.price_impact_function(self.price_impact_model)(delayed_supply, virtual_tank)

    def generate_gbm_increments(self, dt=simulation_configuration.DELTA_TIME,
                                timesteps=simulation_configuration.TIMESTEPS):
        # TODO remove hardcoded blocks per year use simulation_configuration
        blocks_per_year = 365 * 24 * 60 * 60 // blocktime_seconds
        timesteps_per_year = blocks_per_year // dt
        per_timestep_volatility = self.volatility / np.sqrt(timesteps_per_year)
        print(self.drift)
        process = processes.continuous.GeometricBrownianMotion(
            drift=self.drift,
            volatility=per_timestep_volatility,
            t=1,
            rng=np.random.default_rng(1)
        )
        self. increments = process.sample(timesteps * dt + 1)[1:]

    # Todo add delay that creates time lag between Mento trades and price impact

    def impact_delay(self, block_supply_change,
                     impact_delay=ImpactDelay.INSTANT,
                     dt=simulation_configuration.DELTA_TIME,
                     timesteps=simulation_configuration.TIMESTEPS):
        if impact_delay == ImpactDelay.INSTANT:
            unit_array = np.zeros(timesteps * dt + 1)
            def delay_envelope(x): return x * unit_array
            self.supply_changes += delay_envelope(block_supply_change)

    def historical_returns(self, sample_size, seed):
        """Creates a random sample from a set of historical log-returns
        """
    # TODO Consider different sampling options
        random.seed(seed)
        samples = random.choices(self.historical_data, sample_size)
        self.increments = samples

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

    def gbm(self, dt=simulation_configuration.DELTA_TIME, timesteps=simulation_configuration.TIMESTEPS):
        # dt=simulation_configuration.DELTA_TIME,):
        blocks_per_year = 365 * 24 * 60 * 60 // blocktime_seconds
        timesteps_per_year = blocks_per_year // dt
        per_timestep_volatility = self.volatility / np.sqrt(timesteps_per_year)
        process = processes.continuous.GeometricBrownianMotion(
            drift=self.drift,
            volatility=per_timestep_volatility,
            t=1,
            rng=np.random.default_rng(1)
        )

    def update(self):
        self.demand = 0.5
