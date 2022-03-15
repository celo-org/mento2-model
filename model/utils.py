"""
Misc. utility and helper functions
"""

import copy
from dataclasses import field
from functools import partial
import numpy as np

import pandas as pd


def _update_from_signal(
    state_variable,
    signal_key,
    _params,
    _substep,
    _state_history,
    _previous_state,
    policy_input,
):
    return state_variable, policy_input[signal_key]


def update_from_signal(state_variable, signal_key=None):
    """A generic State Update Function to update a State Variable directly from a Policy Signal

    Args:
        state_variable (str): State Variable key
        signal_key (str, optional): Policy Signal key. Defaults to None.

    Returns:
        Callable: A generic State Update Function
    """
    if not signal_key:
        signal_key = state_variable
    return partial(_update_from_signal, state_variable, signal_key)


def local_variables(_locals):
    return {
        key: _locals[key]
        for key in [_key for _key in _locals.keys() if "__" not in _key]
    }


def default(obj):
    return field(default_factory=lambda: copy.copy(obj))


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
DATA_FOLDER = '/Users/sissnad/celo/reviews/mento2-model/data/'
data_feed = DataFeed(DATA_FOLDER)
data_feed.load_historical_data('mock_logreturns.csv')
