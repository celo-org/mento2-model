"""
python replication to debug the mento notebook
"""
# Import the setup module:
# * sets up the Python path
# * runs shared notebook-configuration methods, such as loading IPython modules
# import setup
import sys
import copy
from model import constants # import needed for initialization to avoid circular import later
from experiments import default_experiment
from pprint import pprint
from experiments.run import run
sys.path.append("../..")
sys.path.append("../../..")

simulation_analysis_1 = copy.deepcopy(default_experiment.experiment.simulations[0])

simulation_analysis_1.model.params.update({
    "reserve_fraction": [0.001, 0.01],
})

pprint(simulation_analysis_1.model.initial_state)

pprint(simulation_analysis_1.model.params)

df, exceptions = run(simulation_analysis_1)
