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

DATA_FOLDER = Path(__file__, "../../../data/").resolve()
DATA_FILE_NAME = "mock_logreturns.prq"

# pylint: disable = too-few-public-methods


class DataFeed:
    """
    Performs data conversion for generators
    """

    def __init__(self, data_folder, data_file_name):
        self.data_folder = data_folder
        self.historical_data = pd.read_parquet(Path(self.data_folder, data_file_name))
        self.data = np.array(self.historical_data)
        self.length = len(self.historical_data)
        self.assets = list(self.historical_data.columns)
