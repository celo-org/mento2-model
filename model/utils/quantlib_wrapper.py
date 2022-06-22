"""
This module provides a wrapper class for the required QuantLib functionality
"""
from typing import List
import numpy as np

from QuantLib import (TimeGrid, StochasticProcessArray,
                      UniformRandomGenerator, UniformRandomSequenceGenerator,
                      GaussianRandomSequenceGenerator, GaussianMultiPathGenerator)

from experiments import simulation_configuration
from model import constants
from model.types.configs import MarketPriceConfig

# raise numpy warnings as errors
np.seterr(all='raise')


class QuantLibWrapper():
    """
    This class wraps part of QuantLib to create increments
    """

    processes: List[MarketPriceConfig]
    correlations: List[List[float]]
    initial_value: float
    number_of_paths_per_asset: int

    def __init__(self, processes, correlation, sample_size, seed):
        self.processes = processes
        self.correlation = correlation
        # as we use the log returns of each process initial value is irrelevant for processes
        # with independent multiplicative increments
        self.initial_value = 1
        self.number_of_paths_per_asset = 1
        self.timesteps_per_year = (constants.blocks_per_year /
                                   simulation_configuration.BLOCKS_PER_TIMESTEP)
        self.sample_size = sample_size
        self.seed = seed

    def process_container(self):
        """
        Creates an array of processes
        """

        processes = [config.process(
            self.initial_value,
            config.param_1 / self.timesteps_per_year,
            config.param_2 / np.sqrt(self.timesteps_per_year))
            for config in self.processes]
        process_array = StochasticProcessArray(processes, self.correlation)
        return process_array

    def correlated_returns(self):
        log_returns = self.generate_correlated_paths()
        increments = {}
        for config, path in zip(self.processes, log_returns):
            increments[config.pair] = path
        return increments

    # pylint: disable = too-many-locals
    def generate_correlated_paths(self):
        """
        Generates paths
        """
        process = self.process_container()
        time_grid = TimeGrid(self.sample_size, self.sample_size)
        if isinstance(process, StochasticProcessArray):
            # time points are not really required for block step size but will if we change
            # to other time delta
            time_points = []
            for index, _time in enumerate(time_grid):
                time_points.append(time_grid[index])
            steps = (len(time_points) - 1) * process.size()
            sequence_generator = UniformRandomSequenceGenerator(
                steps, UniformRandomGenerator(seed=self.seed))
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
