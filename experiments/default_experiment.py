"""
The default experiment with default model, Initial State, System Parameters, and Simulation Configuration.

The defaults are defined in their respective modules:
* Initial State in `model/state_variables.py`
* System Parameters in `model/system_parameters.py`
* Simulation Configuration in `experiments/simulation_configuration.py`
"""

import re

from typing import List, Type, Dict, Any
from radcad import Simulation, Experiment, Backend
from radcad.core import generate_parameter_sweep
from radcad.wrappers import Context, Model

from model import model
from experiments.simulation_configuration import TIMESTEPS, MONTE_CARLO_RUNS
from model.components import ModelComponent
from model.components.markets import MarketPriceComponent

class SimulationWithComponents(Simulation):
    components: List[Type[ModelComponent]]

    def __init__(self, model: Model, timesteps=100, runs=1, components: List[Type[ModelComponent]]=[], **kwargs):
        super().__init__(model, timesteps, runs, **kwargs)
        self.before_subset = self.__before_subset__
        self.components = components

    def __before_subset__(self, context: Context = None):
        param_sweep = generate_parameter_sweep(context.parameters)
        params = param_sweep[context.subset]
        print(params)
        context.initial_state.update(self.__setup_components__(params))
    
    def __setup_components__(self, params):
        components_dict = {}
        for component in self.components:
            # MarketPriceComponent => _market_price_component
            component_name = re.sub('([A-Z]+)', r'_\1', component.__name__).lower() 
            component_instance = component.from_parameters(params)
            components_dict[component_name] = component_instance
        return components_dict


# Create Model Simulation
simulation = SimulationWithComponents(
    model=model,
    timesteps=TIMESTEPS,
    runs=MONTE_CARLO_RUNS,
    components=[MarketPriceComponent]
)
# Create Experiment of single Simulation
experiment = Experiment([simulation])
# Configure Simulation & Experiment engine
simulation.engine = experiment.engine
experiment.engine.backend = Backend.SINGLE_PROCESS
experiment.engine.deepcopy = False
experiment.engine.drop_substeps = True  # Do not store data for substeps
