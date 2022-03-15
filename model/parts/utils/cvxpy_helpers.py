"""
Helpers for using cvxpy as optimization tool for actor decisions
"""
from cvxpy import Parameter


def turn_dict_to_cvxpy_params_dict(state_variables_or_params_dict):
    """
    Turn all numerical radCAD prev_state (or params) values into a cvxpy_params dict that contains
    all radCAD state variables (or radCAD params) as cvxpy Parameter type
    """
    # TODO: Allow more than 2 levels of depth
    cvxpy_dict = dict()
    for key, value in state_variables_or_params_dict.items():
        if type(value) == int or type(value) == float:
            cvxpy_dict[key] = value
        elif type(value) == dict:
            cvxpy_dict[key] = {}
            for subkey, subvalue in value.items():
                if not type(subvalue) == dict:
                    cvxpy_dict[key][subkey] = subvalue
    return cvxpy_dict
