# %% [markdown]
# # Experiment README

# %% [markdown]
# ## Table of Contents
#
# * [Overview of Experiment Architecture](#Overview-of-Experiment-Architecture)
# * [Experiment Workflow](#Experiment-Workflow)
#     * [Modifying State Variables](#Modifying-State-Variables)
#     * [Modifying System Parameters](#Modifying-System-Parameters)
#     * [Executing Experiments](#Executing-Experiments)
#     * [Post-processing and Analysing Results](#Post-processing-and-Analysing-Results)
#     * [Visualizing Results](#Visualizing-Results)
# * [Creating New, Customized Experiment Notebooks](#Creating-New,-Customized-Experiment-Notebooks)
#     * Step 1: Select an experiment template
#     * Step 2: Create a new notebook
#     * Step 3: Customize the experiment
#     * Step 4: Execute the experiment
# * [Advanced Experiment-configuration & Simulation Techniques](#Advanced-Experiment-configuration-&-Simulation-Techniques)
#     * [Setting Simulation Timesteps and Unit of Time `dt`](#Setting-Simulation-Timesteps-and-Unit-of-Time-dt)
#     * [Changing the Ethereum Network Upgrade Stage](#Changing-the-Ethereum-Network-Upgrade-Stage)
#     * [Performing Large-scale Experiments](#Performing-Large-scale-Experiments)

# %% [markdown]
# # Overview of Experiment Architecture
#
# The experiment architecture is composed of the following four elements – the **model**, **default experiment**, **experiment templates**, and **experiment notebooks**:
#
# 1. The **model** is initialized with a default Initial State and set of System Parameters defined in the `model` module.
# 2. The **default experiment** – in the `experiments.default_experiment` module – is an experiment composed of a single simulation that uses the default cadCAD **model** Initial State and System Parameters. Additional default simulation execution settings such as the number of timesteps and runs are also set in the **default experiment**.
# 3. The **experiment templates** – in the `experiments.templates` module – contain pre-configured analyses based on the **default experiment**. Examples include... To be created!
# 4. The **experiment notebooks** perform various scenario analyses by importing existing **experiment templates**, optionally modifying the Initial State and System Parameters within the notebook, and then executing them.

# %% [markdown]
# # Experiment Workflow
#
# If you just want to run (execute) existing experiment notebooks, simply open the respective notebook and execute all cells.

# %% [markdown]
# Depending on the chosen template and planned analysis, the required imports might differ slightly from the below standard dependencies:

# %%
# Import the setup module:
# * sets up the Python path
# * runs shared notebook-configuration methods, such as loading IPython modules
from radcad import Experiment, Engine, Backend
from model.types import Stage
from experiments.simulation_configuration import TIMESTEPS, DELTA_TIME
from stochastic.processes.continuous import FractionalBrownianMotion
import matplotlib.pyplot as plt
import experiments.templates.monte_carlo_analysis as monte_carlo_analysis
import setup

# External dependencies
import copy
import logging
import pandas as pd
import plotly.express as px
from pprint import pprint
import importlib as imp

# Project dependencies
import model.constants as constants
from experiments.run import run
from experiments.utils import display_code
import experiments.notebooks.visualizations as visualizations

# %% [markdown]
# We can then import the default experiment, and create a copy of the simulation object – we create a new copy for each analysis we'd like to perform:

# %%
import experiments.default_experiment as default_experiment
simulation_analysis_1 = copy.deepcopy(default_experiment.experiment.simulations[0])

# %% [markdown]
# We can use the `display_code` method to see the configuration of the default experiment before making changes:

# %%
# In this example equivalent to display_code(simulation_analysis_1.)
display_code(default_experiment)

# %% [markdown]
# Alternatively to modifying the default experiment in a notebook as shown in the next section, we can also load predefined experiment templates:

# %%
simulation_analysis_2 = copy.deepcopy(monte_carlo_analysis.experiment.simulations[0])
display_code(monte_carlo_analysis)

# %% [markdown]
# ## Modifying State Variables

# %% [markdown]
# To view what the Initial State (radCAD model-configuration setting `initial_state`) of the State Variables are, and to what value they have been set, we can inspect the dictionary as follows:

# %%
pprint(simulation_analysis_1.model.initial_state)

# %%
simulation_analysis_1.model.state

# %% [markdown]
# To modify the value of **State Variables** for a specific analysis, you need to select the relevant simulation and update the chosen model Initial State. For example, updating the `floating_supply` Initial State to `100e6` CELO and `123e5` cUSD.

# %%
simulation_analysis_1.model.initial_state.update({
    'floating_supply': {
        'celo': 100e6,
        'cusd': 123e5},
})

# %%
simulation_analysis_1.model.initial_state.update({
    'market_price': {
        'usd': 1},
})

# %%
simulation_analysis_1.model.initial_state['_market_price_generator'].volatility


# %%


fbm = FractionalBrownianMotion(hurst=0.7, t=1)

fbm.sample(3)

# %% [markdown]
# Show updated initial `floating_supply`:

# %%
pprint(simulation_analysis_1.model.initial_state)

# %% [markdown]
# ## Modifying System Parameters

# %% [markdown]
# To view what the System Parameters (radCAD model configuration setting `params`) are, and to what value they have been set, we can inspect the dictionary as follows:

# %%
pprint(simulation_analysis_1.model.params)

# %% [markdown]
# To modify the value of **System Parameters** for a specific analysis, you need to select the relevant simulation, and update the chosen model System Parameter (which is a list of values). For example, updating the `reserve_fraction` System Parameter to a sweep of two values, `0.001` and `0.01`:

# %%
simulation_analysis_1.model.params.update({
    "reserve_fraction": [0.001, 0.1],
})

# %% [markdown]
# ## Executing Experiments

# %% [markdown]
# We can now execute our custom analysis and retrieve the post-processed Pandas DataFrame using the `run(...)` method:

# %%
df, exceptions = run(simulation_analysis_1)

# %% [markdown]
# ## Post-processing and Analysing Results

# %% [markdown]
# We can see that we had no exceptions for the single simulation we executed:

# %%
exceptions[0]['exception'] == None

# %% [markdown]
# We can simply display the Pandas DataFrame to inspect the results. This DataFrame already has some default post-processing applied (see [experiments/post_processing.py](../post_processing.py)). For example, parameters that change in the parameter grid (if there are any) are attached as columns to the end of the dataframe.

# %%
# Show which reserve_fraction values were used in the grid
df.groupby('subset')['reserve_fraction'].unique()

# %% [markdown]
# We can also use Pandas for numerical analyses:

# %%
# Get the maximum mento_rate for each subset: in this example each reserve_fraction value used in the grid.
df.groupby('subset')['mento_rate'].max()

# %% [markdown]
# ## Visualizing Results

# %% [markdown]
# Once we have the results post-processed and in a Pandas DataFrame, we can use Plotly for plotting our results:

# %%
# Plot the mento_rate for each subset (each parameter grid combination)
px.line(df, x='timestep', y='mento_rate', facet_col='subset')

# %%
# Plot using visualizations predefined in the visualizations module
visualizations.plot_celo_price(df)

# %% [markdown]
# # Creating New, Customized Experiment Notebooks
#
# If you want to create an entirely new analysis, you'll need to create a new experiment notebook, which entails the following steps:
# * Step 1: Select an experiment template from the `experiments/templates/` directory to start from. If you'd like to create your own template, the [example_analysis.py](../templates/example_analysis.py) template gives an example of extending the default experiment to override default State Variables and System Parameters that you can copy.
# * Step 2: Create a new notebook in the `experiments/notebooks/` directory, using the [template.ipynb](./template.ipynb) notebook as a guide, and import the experiment from the experiment template.
# * Step 3: Customize the experiment for your specific analysis.
# * Step 4: Execute your experiment, post-process and analyze the results, and create Plotly charts!

# %% [markdown]
# # Advanced Experiment-configuration & Simulation Techniques

# %% [markdown]
# ## Setting Simulation Timesteps and Unit of Time `dt`

# %%

# %% [markdown]
# We can configure the number of simulation timesteps `TIMESTEPS` from a `simulation_time_seconds` divided by the product of `blocktime_seconds` and the number of blocks per timestep `DELTA_TIME`:

# %% [markdown]
# `DELTA_TIME` is a variable that sets how many blocks are simulated for each timestep. Sometimes, if we don't need a finer granularity (1 block per timestep, for example), we can then set `DELTA_TIME` to a larger integer value for better performance. The default value is 1 block per timestep which means we simulate on a per block basis.

# %% [markdown]
# ```python
# simulation_time_seconds = 365 * 24 * 60 * 60  # If we choose 1 year
# TIMESTEPS = simulation_time_seconds // (constants.blocktime_seconds * DELTA_TIME)
# ```

# %%
TIMESTEPS

# %% [markdown]
# Finally, to set the simulation timesteps (note, additionally you may have to update the environmental processes that depend on the number of timesteps, and override the relevant parameters):

# %%
simulation_analysis_1.timesteps = TIMESTEPS

# %% [markdown]
# ## Changing the Mento1 -> Mento2 Upgrade Stage

# %% [markdown]
# The model operates over different Mento1 -> Mento2 upgrade stages. The default experiment operates in the "mento1" stage (so no upgrades).
#
# `Stage` is an Enum; we can import it and see what options we have:

# %%

# %% [markdown]
# The model is well documented, and we can view the Python docstring to see what a Stage is, and create a dictionary to view the Enum members:

# %%
print(Stage.__doc__)
{e.name: e.value for e in Stage}

# %% [markdown]
# The `Mento1` stage, for example, assumes the mento1 setup w/o stability providers, IRPS, etc.

# %%
display_code(Stage)

# %% [markdown]
# As before, we can update the "stage" System Parameter to set the relevant Stage:

# %%
simulation_analysis_1.model.params.update({
    "stage": [Stage.Mento1]
})

# %% [markdown]
# ## Performing Large-scale Experiments (NOT WORKING YET!)

# %% [markdown]
# When executing an experiment, we have three degrees of freedom - **simulations, runs, and subsets** (parameter sweeps).
#
# We can have multiple simulations for a single experiment, multiple runs for every simulation, and we can have multiple subsets for every run. Remember that `simulation`, `run`, and `subset` are simply additional State Variables set by the radCAD engine during execution – we then use those State Variables to index the results for a specific dimension, e.g. simulation 1, run 5, and subset 2.
#
# Each dimension has a generally accepted purpose:
# * Simulations are used for A/B testing
# * Runs are used for Monte Carlo analysis
# * Subsets are used for parameter sweeps
#
# In some cases, we break these "rules" to allow for more degrees of freedom or easier configuration.
#
# One example of this is the `eth_price_eth_staked_grid_analysis` experiment template we imported earlier:

# %%
display_code(eth_price_eth_staked_grid_analysis)

# %% [markdown]
# Here, we create a grid of two State Variables – ETH price and ETH staked – using the `eth_price_process` and `eth_staked_process`.
#
# Instead of sweeping the two System Parameters to create different subsets, we pre-generate all possible combinations of the two values first and use the specific `run` to index the data, i.e. for each run we get a new ETH price and ETH staked sample.
#
# This allows the experimenter (you!) to use a parameter sweep on top of this analysis if they choose, and we have kept one degree of freedom.

# %% [markdown]
# ### Composing an Experiment Using **simulations, runs, and subsets**

# %%


# Create a new Experiment of three Simulations:
# * Simulation Analysis 1 has one run and two subsets – a parameter sweep of two values (BASE_REWARD_FACTOR = [64, 32])
# * Simulation Analysis 2 has one run and one subset – a basic simulation configuration
# * Simulation Analysis 3 has 400 runs (20 * 20) and one subset – a parameter grid indexed using `run`
experiment = Experiment(
    [simulation_analysis_1, simulation_analysis_2, simulation_analysis_3])

# %% [markdown]
# ### Configuring the radCAD Engine for High Performance
#
# To improve simulation performance for large-scale experiments, we can set the following settings using the radCAD `Engine`. Both Experiments and Simulations have the same `Engine`; when executing an `Experiment` we set these settings on the `Experiment` instance:

# %%
# Configure Experiment Engine
experiment.engine = Engine(
    # Use a single process; the overhead of creating multiple processes
    # for parallel-processing is only worthwhile when the Simulation runtime is long
    backend=Backend.SINGLE_PROCESS,
    # Disable System Parameter and State Variable deepcopy:
    # * Deepcopy prevents mutation of state at the cost of lower performance
    # * Disabling it leaves it up to the experimenter to use Python best-practises to avoid
    # state mutation, like manually using `copy` and `deepcopy` methods before
    # performing mutating calculations when necessary
    deepcopy=False,
    # If we don't need the state history from individual substeps,
    # we can get rid of them for higher performance
    drop_substeps=True,
)

# Disable logging
# For large experiments, there is lots of logging. This can get messy...
logger = logging.getLogger()
logger.disabled = True

# Execute Experiment
raw_results = experiment.run()

# %% [markdown]
# ### Indexing a Large-scale Experiment Dataset

# %%
# Create a Pandas DataFrame from the raw results
df = pd.DataFrame(experiment.results)
df

# %%
# Select each Simulation dataset
df_0 = df[df.simulation == 0]
df_1 = df[df.simulation == 1]
df_2 = df[df.simulation == 2]

datasets = [df_0, df_1, df_2]

# Determine size of Simulation datasets
for index, data in enumerate(datasets):
    runs = len(data.run.unique())
    subsets = len(data.subset.unique())
    timesteps = len(data.timestep.unique())

    print(
        f"Simulation {index} has {runs} runs * {subsets} subsets * {timesteps} timesteps = {runs * subsets * timesteps} rows")

# %%
# Indexing simulation 0, run 1 (indexed from one!), subset 1, timestep 1
df.query("simulation == 0 and run == 1 and subset == 1 and timestep == 1")
