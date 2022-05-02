import itertools
import math
from datetime import datetime

import pandas as pd
import plotly.express as px

# Set plotly as the default plotting backend for pandas
pd.options.plotting.backend = "plotly"


def plot_celo_market_price(df):

    fig = px.line(df, x='timestep', y='market_price_celo_usd', color='run', facet_col='subset',
                  title='CELO price')
    return fig

def plot_celo_floating_supply(df):
    """
    Plot the celo floating supply for each subset (each parameter grid combination)
    :param df: simulation output dataframe after postprocessing
    :return: plotly express fig
    """
    fig = px.line(df, x='timestep', y='floating_supply_celo', color='run', facet_col='subset',
                  title='Floating supply CELO')
    return fig

def plot_reserve_balance(df):
    """
    Plot the celo reserve balance for each subset (each parameter grid combination)
    :param df: simulation output dataframe after postprocessing
    :return: plotly express fig
    """
    fig = px.line(df, x='timestep', y='reserve_balance_celo', color='run', facet_col='subset',
                  title='reserve balance CELO')
    return fig

def plot_mento_rate(df):
    """
    Plot the mento rate for each subset (each parameter grid combination)
    :param df: simulation output dataframe after postprocessing
    :return: plotly express fig
    """
    fig = px.line(df, x='timestep', y='mento_rate', color='run', facet_col='subset',
                  title='Mento rate')
    return fig
