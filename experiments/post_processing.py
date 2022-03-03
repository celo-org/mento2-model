import pandas as pd
from radcad.core import generate_parameter_sweep

from model.system_parameters import parameters, Parameters


def assign_parameters(df: pd.DataFrame, parameters: Parameters, set_params=[]):
    if set_params:
        parameter_sweep = generate_parameter_sweep(parameters)
        parameter_sweep = [{param: subset[param]
                            for param in set_params} for subset in parameter_sweep]

        for subset_index in df['subset'].unique():
            for (key, value) in parameter_sweep[subset_index].items():
                df.loc[df.eval(f'subset == {subset_index}'), key] = value
    return df


def post_process(df: pd.DataFrame, drop_timestep_zero=True, parameters=parameters):
    # Show parameters that have taken more than one value in df
    grid_keys = []
    for key, value in parameters.items():
        if len(value) > 1:
            grid_keys.append(key)

    assign_parameters(df, parameters, grid_keys)

    return df
