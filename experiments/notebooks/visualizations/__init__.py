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


def plot_celo_price(df):

    fig = px.line(df, x='timestep', y='mento_rate', facet_col='subset')
    return fig
