"""
DataFeed class used for loading and parsing of
historical data required by the simulation.
"""
from pathlib import Path
import os
import numpy as np
import pandas as pd

from experiments.simulation_configuration import DATA_SOURCE
# pylint: disable = unused-import
# pylint: disable = redefined-outer-name
import data.mock_data  # this is necessary to create mock data if not existent

DATA_FOLDER = Path(__file__, "../../../data/").resolve()
MOCK_DATA_FILE_NAME = "mock_logreturns.prq"
HISTORICAL_DATA_FILE_NAME = "historical_market_data/cusd_celo_example.csv"

# pylint: disable = too-few-public-methods


class DataFeed:
    """
    Performs data conversion for generators
    """

    def __init__(self, data_folder):
        self.data_folder = data_folder

        if DATA_SOURCE == 'mock':
            self.historical_data = self.load_mock_data(MOCK_DATA_FILE_NAME)
        elif DATA_SOURCE == 'historical':
            self.historical_data = self.load_historical_data(HISTORICAL_DATA_FILE_NAME)
        else:
            raise NotImplementedError("Data source not supported")

        self.data = np.array(self.historical_data[['cusd_usd', 'celo_usd']])
        self.length = len(self.historical_data)
        self.assets = list(self.historical_data.columns)

    def load_mock_data(self, data_file_name):
        """
        loads mock logreturns as generated in data/mock_data.py
        """
        mock_data = pd.read_parquet(Path(self.data_folder, data_file_name))
        return mock_data

    def load_historical_data(self, data_file_name):
        """
        loads historical data for cusd_usd and celo_usd from one file
        currently .csv and .prq file extensions are supported
        """
        if data_file_name.endswith('.prq'):
            historical_prices = pd.read_parquet(Path(self.data_folder, data_file_name))
        elif data_file_name.endswith('.csv'):
            historical_prices = pd.read_csv(Path(self.data_folder, data_file_name))
        else:
            _, file_extension = os.path.splitext(data_file_name)
            raise NotImplementedError(f"File extension {file_extension} not supported")

        historical_log_returns = self.calculate_log_returns(historical_prices)
        return historical_log_returns

    def calculate_log_returns(self, data_frame):
        """
        calculates log returns out of a data frame with price time series in its columns
        """
        return data_frame.apply(lambda column: np.log((column/column.shift(1)).dropna()))
