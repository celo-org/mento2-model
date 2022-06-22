# ⚠ ️Project moved to [mento-protocol/simulation](https://github.com/mento-protocol/simulation). This repo is archived. ⚠️

# cLabs Mento2 Model

A modular dynamical-systems model of the Mento2.0 design, based on the open-source Python library [radCAD](https://github.com/CADLabs/radCAD), an extension to [cadCAD](https://cadcad.org).

* Latest model release version: [Private fork of Ethereum Economic Model / v0.0.0](https://github.com/celo-org/mento2-model/releases/tag/v0.0.0)

## Table of Contents

* [Introduction](#Introduction)
  * [Model Features](#Model-Features)
  * [Directory Structure](#Directory-Structure)
  * [Model Architecture](#Model-Architecture)
  * [Model Assumptions](#Model-Assumptions)
  * [Mathematical Model Specification](#Mathematical-Model-Specification)
  * [Differential Model Specification](#Differential-Model-Specification)
* [Environment Setup](#Environment-Setup)
* [Simulation Experiments](#Simulation-Experiments)
* [Model Extension Roadmap](#Model-Extension-Roadmap)
* [Tests](#Tests)
* [Change Log](#Change-Log)
* [Acknowledgements](#Acknowledgements)
* [Contributors](#Contributors-)
* [License](#License)

---

## Introduction

This repo features a cadCAD model for Mento2.0. The structure of this repo is heavily based on the [Ethereum Economic Model](https://github.com/CADLabs/ethereum-economic-model).

### Model Features

* Configurable to reflect protocol behaviour at different points in time of the development roadmap (referred to as "upgrade stages"):
  * Exchange update?
  * Reserve update?
  * ...
* Flexible calculation granularity: By default, State Variables, System Metrics, and System Parameters are calculated at block level and aggregated per epoch. Users can easily change epoch aggregation using the delta-time (`dt`) parameter. The model can be extended for slot-level granularity and analysis if that is desired (see [Model Extension Roadmap](#Model-Extension-Roadmap)).
* Supports [state-space analysis](https://en.wikipedia.org/wiki/State-space_representation) (i.e. simulation of system state over time) and [phase-space analysis](https://en.wikipedia.org/wiki/Phase_space) (i.e. generation of all unique system states in a given experimental setup).
* Customizable processes to set important variables such as CELO price, CELO staked, and gas pricing.
* Modular model structure for convenient extension and modification. This allows different user groups to refactor the model for different purposes, rapidly test new incentive mechanisms, or update the model as CELO implements new protocol improvements.
* References to official [Mento 2.0 specs (non-existent at this point!)](https://github.com/still-to-be-created) in Policy and State Update Function logic. This enables seamless onboarding of protocol developers and allows the more advanced cadCAD user to dig into the underlying protocol design that inspired the logic.

### Directory Structure

* [data/](data/): Datasets and API data sources used in the model
* [docs/](docs/): Misc. documentation such as auto-generated docs from Python docstrings and Markdown docs
* [experiments/](experiments/): Analysis notebooks and experiment workflow (such as configuration and execution)
* [logs/](logs/): Experiment runtime log files
* [model/](model/): Model software architecture (structural and configuration modules)
* [tests/](tests/): Unit and integration tests for model and notebooks

### Model Architecture

The [model/](model/) directory contains the model's software architecture in the form of two categories of modules: structural modules and configuration modules.

#### Structural Modules

The model is composed of several structural modules in the [model/parts/](model/parts/) directory:

| Module | Description |
| --- | --- |
| [celo_system.py](model/parts/celo_system.py) | General CELO mechanisms, such as managing the system upgrade process, the gas pricing mechanism, and updating the CELO price and CELO supply |
| [reserve.py](model/parts/buy_and_sell.py) | Calculation of the mechanics when interacting with the CELO reserve |
| [system_metrics.py](model/parts/system_metrics.py) | Calculation of metrics such as stability provider rewards |

#### Configuration Modules

The model is configured using several configuration modules in the [model/](model/) directory:

| Module | Description |
| --- | --- |
| [constants.py](model/constants.py) | Constants used in the model, e.g. number of blocks per epoch, Gwei in 1 CELO |
| [state_update_blocks.py](model/state_update_blocks.py) | cadCAD model State Update Block structure, composed of Policy and State Update Functions |
| [state_variables.py](model/state_variables.py) | Model State Variable definition, configuration, and defaults |
| [stochastic_processes.py](model/stochastic_processes.py) | Helper functions to generate stochastic environmental processes |
| [system_parameters.py](model/system_parameters.py) | Model System Parameter definition, configuration, and defaults |
| [types.py](model/types.py) | Various Python types used in the model, such as the `Stage` Enum and calculation units |
| [utils.py](model/utils.py) | Misc. utility and helper functions |

### Model Assumptions

The model implements the official Ethereum Specification wherever possible, but rests on a few default network-level and validator-level assumptions detailed in the [ASSUMPTIONS.md](ASSUMPTIONS.md) document.

### Mathematical Model Specification

The [Mathematical Model Specification](https://hackmd.io/@CADLabs/ryLrPm2T_) articulates the relevant system dynamics as a state-space representation, the mathematical modelling paradigm underlying the cadCAD simulation library. It can be understood as a minimum viable formalism necessary to enable solid cadCAD modelling.

### Differential Model Specification

The [Differential Model Specification](https://hackmd.io/@CADLabs/HyENPQ36u) depicts the model's overall structure across System States, System Inputs, System Parameters, State Update Logic and System Metrics.

## Environment Setup

1. Clone or download the Git repository: `git clone https://github.com/celo-org/mento2-model` or using GitHub Desktop
2. Set up your development environment using one of the following two options:

### Option 1: Your usual python workflow

You can use your usual python workflow and install dependencies from the [Pipfile](Pipfile), for example using `virtualenv`
or `Anaconda`.

### Option 2: Using [Pyenv](https://github.com/pyenv/pyenv) and [Pipenv](https://github.com/pypa/pipenv)

Our usual python workflow is with Pyenv and Pipenv. Pyenv is a package to manage different versions of python
and Pipenv automatically creates virtual environments and installs and updates packages and dependencies. In your shell:

1) Install [Pyenv](https://github.com/pyenv/pyenv)
2) Install [Pipenv](https://github.com/pypa/pipenv)
3) Navigate to your `\mento2-model` folder
4) install python 3.8.12: `pyenv install  3.8.12`
5) Set your local python version `pyenv local  3.8.12`
7) Install dependencies: `pipenv install --dev`
8) Enter virtual environment: `pipenv shell`
9) Local pre-commit setup: `pre-commit install`
10) Install your virtual environment as jupyter kernel: `python -m ipykernel install --user --name=mento2-model`

To start Jupyter Notebook or Lab:
```bash
jupyter notebook
# Or:
jupyter lab
```

## Simulation Experiments

The [experiments/](experiments/) directory contains modules for configuring and executing simulation experiments, as well as performing post-processing of the results.

The [experiments/notebooks/](experiments/notebooks/) directory contains initial Mento experiment notebooks and analyses. These notebooks and analyses do not aim to comprehensively illuminate the Celo and Mento protocols, but rather to suggest insights into a few salient questions the Celo and Mento community has been discussing, and to serve as inspiration for researchers building out their own, customized analyses and structural model extensions.

The [Experiment README notebook](experiments/notebooks/0_README.ipynb) contains an overview of how to execute existing experiment notebooks, and how to configure and execute new ones.

#### Notebook 1. Model Validation

Could potentially contain a backtest of a Mento 1.0 model against empirical data.

#### Notebook 2. Stability Provider Analysis

The purpose of this notebook is to explore the risks & returns that stability providers can expect.

[comment]: <> (* Analysis 1: )

[comment]: <> (* Analysis 2: )

#### Notebook 3. Arbitrage Provider Analysis

The purpose of this notebook is to explore the risks & returns that arbitrage providers can expect.

[comment]: <> (* Analysis: Inflation Rate and ETH Supply Over Time)

## Model Extension Roadmap

Nothing here yet.

## Tests

We use Pytest to test the `model` module code, as well as the notebooks.

To execute the Pytest tests:
```bash
source venv/bin/activate
python3 -m pytest tests
```

To run the full GitHub Actions CI Workflow (see [.github/workflows](.github/workflows)):
```bash
source venv/bin/activate
make test
```

## Acknowledgements

This Mento 2.0 analysis is a fork of the [Ethereum Economic Model](https://github.com/CADLabs/ethereum-economic-model). We actively try to stay as close as possible to the structure of the Ethereum Economic Model to make it easier for the broader community to follow our analysis.

Since we borrow so heavily from previous work, we would like to thank:
* [Ethereum Ecosystem Support Program](https://esp.ethereum.foundation/en/) for sponsoring the work on the Ethereum Economic Model and everyone who contributed to it.

## Contributors ✨

## License
The code repository `celo-org/mento2-model` is licensed under the GNU General Public License v3.0.
Permissions of this strong copyleft license are conditioned on making available complete source code of licensed works and modifications, which include larger works using a licensed work under the same license. Copyright and license notices must be preserved. Contributors provide an express grant of patent rights.
If you'd like to cite this code and/or research, we suggest the following format:
> cLabs, Mento2 Model, (2021), GitHub repository, https://github.com/celo-org/mento2-model

```latex

[comment]: <> (@misc{cLabs2022,)

[comment]: <> (  author = {cLabs},)

[comment]: <> (  title = {Mento2 Model},)

[comment]: <> (  year = {2022},)

[comment]: <> (  publisher = {GitHub},)

[comment]: <> (  journal = {GitHub repository},)

[comment]: <> (  howpublished = {\url{https://github.com/celo-org/mento2-model}},)

[comment]: <> (  version = {v0.0.0})

[comment]: <> (})
```
