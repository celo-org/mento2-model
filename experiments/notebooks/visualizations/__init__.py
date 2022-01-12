import itertools
import math
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from ipywidgets import widgets
from plotly.subplots import make_subplots

from experiments.notebooks.visualizations.plotly_theme import (
    cadlabs_colors,
    cadlabs_colorway_sequence,
)
from model.system_parameters import parameters
import model.constants as constants


# Set plotly as the default plotting backend for pandas
pd.options.plotting.backend = "plotly"
