"""
Post processing results
"""

import pandas as pd
from radcad.core import generate_parameter_sweep

from model.system_parameters import parameters as base_parameters, Parameters


def assign_parameters(dataframe: pd.DataFrame, parameters: Parameters, set_params=None):
    """
    parameters that change in the parameter grid (if there are any)
    are attached as columns to the end of the dataframe
    """
    if set_params:
        parameter_sweep = generate_parameter_sweep(parameters)
        parameter_sweep = [{param: subset[param]
                            for param in set_params} for subset in parameter_sweep]

        for subset_index in dataframe['subset'].unique():
            for (key, value) in parameter_sweep[subset_index].items():
                dataframe.loc[dataframe.eval(f'subset == {subset_index}'), key] = value
    return dataframe


def post_process(dataframe: pd.DataFrame, drop_timestep_zero=True, parameters=None):
    """
    Apply post processing functions to simulation output dataframe
    """
    parameters = parameters or base_parameters
    # Show parameters that have taken more than one value in dataframe
    grid_keys = []
    for key, value in parameters.items():
        if len(value) > 1:
            grid_keys.append(key)

    assign_parameters(dataframe, parameters, grid_keys)

    dataframe = dict_to_columns(dataframe)
    dataframe = dataframe.set_index('timestep')

    # Calculate mento rate
    dataframe['mento_rate_cusd_celo'] = (
        dataframe['mento_buckets_cusd_celo.stable']
        / dataframe['mento_buckets_cusd_celo.reserve_asset']
    )
    dataframe['mento_rate_ceur_celo'] = (
        dataframe['mento_buckets_ceur_celo.stable']
        / dataframe['mento_buckets_ceur_celo.reserve_asset']
    )
    dataframe['mento_rate_creal_celo'] = (
        dataframe['mento_buckets_creal_celo.stable']
        / dataframe['mento_buckets_creal_celo.reserve_asset']
    )

    # Drop the initial state for plotting
    if drop_timestep_zero:
        dataframe = dataframe.drop(dataframe.query('timestep == 0').index)

    return dataframe

def dict_to_columns(dataframe):
    """
    Expands dicts to columns in a dataframe
    :param dataframe: pandas dataframe
    :return: pandas dataframe
    """
    for column in dataframe:
        if isinstance(dataframe[column][0], dict):
            expanded_dicts = pd.json_normalize(
                dataframe[column]
            ).add_prefix(f"{dataframe[column].name}_")
            dataframe = pd.concat([dataframe, expanded_dicts], axis=1)
            dataframe = dataframe.drop(columns=column)
    return dataframe
