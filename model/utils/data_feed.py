"""
DataFeed class used for loading and parsing of
historical data required by the simulation.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import data.mock_data # this is necessary to create mock data if not existent


class DataFeed:
    """
    Performs data conversion for generators
    """
    def __init__(self, data_folder):
        self.data_folder = data_folder
        self.data = None
        self.length = None

    def load_historical_data(self, data_file):
        """
        reads historical log returns
        """
        historical_data = pd.read_parquet(Path(self.data_folder, data_file))
        self.data = np.array(historical_data)
        self.length = len(historical_data)


data_folder = Path(__file__, "../../../data/").resolve()
data_file = "mock_logreturns.prq"
