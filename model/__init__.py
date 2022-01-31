"""
Mento2 Model
"""
__version__ = "0.0.1"

import copy
import re
from typing import List, Type

from radcad import Model
from radcad.wrappers import RunArgs
from radcad.core import _single_run_wrapper, generate_parameter_sweep
from model.components.markets import MarketPriceComponent

from model.system_parameters import parameters
from model.state_variables import initial_state
from model.state_update_blocks import state_update_blocks
from model.components import ModelComponent


# Instantiate a new Model
model = Model(
    params=parameters,
    initial_state=initial_state,
    state_update_blocks=state_update_blocks,
)
