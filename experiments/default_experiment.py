"""
The default experiment with default model, Initial State,
System Parameters, and Simulation Configuration.

The defaults are defined in their respective modules:
* Initial State in `model/state_variables.py`
* System Parameters in `model/system_parameters.py`
* Simulation Configuration in `experiments/simulation_configuration.py`
"""

from radcad import Simulation, Experiment, Backend

from experiments.simulation_configuration import TIMESTEPS, MONTE_CARLO_RUNS

from model import model
from model.generators.accounts import AccountGenerator
from model.generators.markets import MarketPriceGenerator
from model.generators.container import container


# Create Model Simulation
simulation = Simulation(
    model=model,
    timesteps=TIMESTEPS,
    runs=MONTE_CARLO_RUNS
)

container.hook_to_simulation(
    simulation, [MarketPriceGenerator, AccountGenerator]
)

# Create Experiment of single Simulation
experiment = Experiment([simulation])

# Configure Simulation & Experiment engine
simulation.engine = experiment.engine
experiment.engine.backend = Backend.SINGLE_PROCESS
experiment.engine.deepcopy = False
experiment.engine.drop_substeps = True  # Do not store data for substeps
