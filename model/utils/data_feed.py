"""
DataFeed class used for loading and parsing of
historical data required by the simulation.
"""
import numpy as np
import pandas as pd

# pylint: disable=too-few-public-methods
class DataFeed:
    """
    Performs data conversion for generators
    """

    # TODO Build data_feed
    def __init__(self, data_folder, data=None, length=0):
        self.data_folder = data_folder
        self.data = data
        self.length = length

    def load_historical_data(self, file_name):
        """
        Parser to read prices and turn them into log-returns"""
        # TODO parser

        if file_name[-3:] == "csv":
            historical_data = pd.read_csv(self.data_folder + file_name)
        elif file_name[-3:] == "prq":
            historical_data = pd.read_parquet(self.data_folder + file_name)
        self.data = np.array(historical_data)
        self.length = len(historical_data)


# TODO Quick and dirt hack to load historical data only once
DATA_FOLDER = '../../data/'
data_feed = DataFeed(DATA_FOLDER)
try:
    data_feed.load_historical_data('mock_logreturns.prq')
except FileNotFoundError as e:
    raise RuntimeError(
        "Run `python data/mock_data.py` to generate the mock_logreturns.prg file"
        ) from e
