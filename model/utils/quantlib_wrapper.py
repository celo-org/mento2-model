"""
This module provides a wrapper class for the required QuantLib functionality
"""
import numpy as np

from QuantLib import (TimeGrid, StochasticProcessArray,
                      UniformRandomGenerator, UniformRandomSequenceGenerator,
                      GaussianRandomSequenceGenerator, GaussianMultiPathGenerator)

from experiments import simulation_configuration
from model import constants

# raise numpy warnings as errors
np.seterr(all='raise')


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
