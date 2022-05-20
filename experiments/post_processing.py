"""
Post processing results
"""

import pandas as pd
from radcad.core import generate_parameter_sweep

from model.system_parameters import parameters, Parameters


def assign_parameters(df: pd.DataFrame, parameters: Parameters, set_params=[]):
    """
    parameters that change in the parameter grid (if there are any) are attached as columns to the end of the dataframe
    """
    if set_params:
        parameter_sweep = generate_parameter_sweep(parameters)
        parameter_sweep = [{param: subset[param]
                            for param in set_params} for subset in parameter_sweep]

        for subset_index in df['subset'].unique():
            for (key, value) in parameter_sweep[subset_index].items():
                df.loc[df.eval(f'subset == {subset_index}'), key] = value
    return df


def post_process(df: pd.DataFrame, drop_timestep_zero=True, parameters=parameters):
    """
    Apply post processing functions to simulation output dataframe
    """
    # Show parameters that have taken more than one value in df
    grid_keys = []
    for key, value in parameters.items():
        if len(value) > 1:
            grid_keys.append(key)

    assign_parameters(df, parameters, grid_keys)

    df = dict_to_columns(df)
    df = df.set_index('timestep')
    df = df.drop(columns=['timestamp'])

    # Calculate mento rate
    df['mento_rate'] = df['mento_buckets_cusd'] / df['mento_buckets_celo']

    # Drop the initial state for plotting
    if drop_timestep_zero:
        df = df.drop(df.query('timestep == 0').index)

    return df

def dict_to_columns(df):
    """
    Expands dicts to columns in a dataframe
    :param df: pandas dataframe
    :return: pandas dataframe
    """
    for column in df:
        if isinstance(df[column][0], dict):
            expanded_dicts = pd.json_normalize(df[column]).add_prefix(f"{df[column].name}_")
            df = pd.concat([df, expanded_dicts], axis=1)
            df = df.drop(columns=column)
    return df
