"""
Default functions for visualization
"""
import itertools
import math
from datetime import datetime

import pandas as pd
import plotly.express as px

from experiments.notebooks.visualizations.plotly_theme import (
    cadlabs_colors,
    cadlabs_colorway_sequence,
)

# Set plotly as the default plotting backend for pandas
pd.options.plotting.backend = "plotly"


def plot_oracle_rate(data_frame):
    """
    Plots oracle rate
    """
    fig = px.line(data_frame, x='timestep', y='oracle_rate', facet_col='subset')
    return fig
