"""
python replication to debug the mento notebook
"""
# Import the setup module:
# * sets up the Python path
# * runs shared notebook-configuration methods, such as loading IPython modules
# import setup
import sys
import copy
sys.path.append("../..")
sys.path.append("../../..")

# External dependencies
from pprint import pprint

# Project dependencies
import model.constants as constants # unused import needed to avoid circular import later
from experiments.run import run

# Project dependencies
import experiments.default_experiment as default_experiment
simulation_analysis_1 = copy.deepcopy(default_experiment.experiment.simulations[0])

pprint(simulation_analysis_1.model.initial_state)

pprint(simulation_analysis_1.model.params)

df, exceptions = run(simulation_analysis_1)
