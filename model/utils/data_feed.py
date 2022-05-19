"""
DataFeed class used for loading and parsing of
historical data required by the simulation.
"""
from pathlib import Path
import numpy as np
import pandas as pd
# pylint: disable = unused-import
# pylint: disable = redefined-outer-name
import data.mock_data  # this is necessary to create mock data if not existent

# pylint: disable=too-few-public-methods


class DataFeed:
    """
    Performs data conversion for generators
    """

    # TODO Build data_feed
    def __init__(self, data_folder, data=None, length=0, assets=None):
        self.data_folder = data_folder
        self.data = data
        self.length = length
        self.assets = assets

    def load_historical_data(self, file_name):
        """
        Parser to read prices and turn them into log-returns"""
        # TODO parser

        if file_name[-3:] == "csv":
            historical_data = pd.read_csv(Path(self.data_folder, file_name))
        elif file_name[-3:] == "prq":
            historical_data = pd.read_parquet(Path(self.data_folder, file_name))
        self.data = np.array(historical_data)
        self.length = len(historical_data)
        self.assets = list(historical_data.columns)


# TODO Quick and dirt hack to load historical data only once
# pylint: disable = redefined-outer-name
data_folder = Path(__file__, "../../../data/")
print(data_folder.resolve())
data_feed = DataFeed(data_folder=data_folder.resolve())
try:
    data_feed.load_historical_data('mock_logreturns.prq')
except FileNotFoundError as e:
    raise RuntimeError(
        "Run `python data/mock_data.py` to generate the mock_logreturns.prg file"
    ) from e
