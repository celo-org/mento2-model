"""
Helpers for using cvxpy as optimization tool for actor decisions
"""
from cvxpy import Parameter


def turn_dict_to_cvxpy_params_dict(state_variables_or_params_dict):
    """
    Turn all numerical radCAD prev_state (or params) values into a cvxpy_params dict that contains
    all radCAD state variables (or radCAD params) as cvxpy Parameter type
    """
    cvxpy_dict = dict()
    for key, value in state_variables_or_params_dict:
        if type(value) == int or type(value) == float:
            cvxpy_dict[key] = Parameter(value=value, pos=True)
        elif type(dict):
            for subkey, subvalue in value:
                if type(subvalue) == int or type(subvalue) == float:
                    cvxpy_dict[key] = Parameter(value=value, pos=True)
    return cvxpy_dict


def cvxpy_param_from_cadcad(params, key, subkey=None, positive=False):
    if subkey:
        cvxpy_param = Parameter(value=params[key][subkey], positive=positive)
    else:
        cvxpy_param = Parameter(value=params[key], positive=positive)

    return cvxpy_param


