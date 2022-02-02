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


class MarketPriceGenerator(Generator):
    def __init__(self, model, drift, volatility, price_impact_model=PriceImpact.CONSTANT_PRODUCT, increments=[None]):
        self.price_impact_model = price_impact_model
        self.model = model
        self.drift = drift
        self.volatility = volatility
        self.increments = self.gbm_increments()
        self.step = 0

    @classmethod
    def from_parameters(cls, parameters):
        if parameters['model'] == MarketPriceModel.GBM:
            return cls(parameters['model'],
                       parameters['drift_market_price'],
                       parameters['volatility_market_price'])
        elif parameters['model'] == MarketPriceModel.PRICE_IMPACT:
            return cls(parameters['model'], None, None)

    @classmethod
    def load_historical_data(cls, file):
        return None

    def observe_market_states(self, state):
        return {'virtual_tank': state['virtual_tanks']['usd'],
                'supply': state['floating_supply']['cusd'],
                'market_price': state['market_price']['cusd_usd']}

    def market_price(self, state):
        if self.model == MarketPriceModel.GBM:
            self.step = + 1
            return state['market_price']['cusd_usd'] * self.increments[self.step]
        elif self.model == MarketPriceModel.PRICE_IMPACT:
            return self.valuate(state['supply'], state['virtual_tank'])
        elif self.model == MarketPriceModel.HIST_SIM:
            self.step = + 1
            return state['market_price']['cusd_usd']*self.increments[self.step]

    def price_impact_function(self, mode):
        return lambda asset_1, asset_2: asset_1 / asset_2
        # elif mode == PriceImpact.CONSTANT_FIAT
        #    return lambda

    def valuate(self, supply, virtual_tank):
        return self.price_impact_function(self.price_impact_model)(supply, virtual_tank)

    def gbm_increments(self, dt=simulation_configuration.DELTA_TIME,
                       timesteps=simulation_configuration.TIMESTEPS):
        blocks_per_year = 365 * 24 * 60 * 60 // blocktime_seconds
        timesteps_per_year = blocks_per_year // dt
        per_timestep_volatility = self.volatility / np.sqrt(timesteps_per_year)
        process = processes.continuous.GeometricBrownianMotion(
            drift=self.drift,
            volatility=per_timestep_volatility,
            t=1,
            rng=np.random.default_rng(1)
        )

        increments = process.sample(timesteps * dt + 1)[1:]
        return increments
    # Todo add delay that creates time lag between Mento trades and price impact

    def impact_delay():
        return None

    def historical_returns(self, sample_size):

        random.choices(self.historical_data, sample_size)
        return

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
