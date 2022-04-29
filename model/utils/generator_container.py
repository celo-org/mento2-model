'''
GeneratorContainer manages the lifecycle of generators running in
the context of a simulation. It ensures generators are initialized
with the right parameters based on the parameter sweep happening
inside radcad and provides a useful decorator to inject them
into policy functions
'''
import functools

from typing import List, Dict, Any
from .generator import Generator

GENERATOR_CONTAINER_PARAM_KEY = '__generator_container__'

# pylint: disable=too-few-public-methods
class GeneratorContainer():
    '''
    The GeneratorContainer used as a singleton
    to manage the lifetimes of generators
    '''

    # Keeps a map of subset -> generator_class_name -> generator_instance
    generators: Dict[str, Generator] = {}
    params: Any

    def __init__(self, params: Any):
        self.params = params

    def get(self, generator_class):
        '''
        Get a generator by subset_id and class with helpful errors
        '''
        assert generator_class is not None, "generator_class is None"
        if self.generators.get(generator_class.__name__) is None:
            self.generators[generator_class.__name__] = \
                generator_class.from_parameters(self.params)

        return self.generators[generator_class.__name__]

def inject(*selector: List[Generator]):
    '''
    Used to wrap policy functions in order to inject generators as arguments, e.g:

    @container.inject(SomeGenerator, SomeOtherGenerator)
    def p_update_policy(params, subset, state_history, prev_state,
                        some_generator, some_other_generator):
        # do things with the generators
        pass
    '''
    def decorator(policy_update_func):
        @functools.wraps(policy_update_func)
        def decor(params, subset, state_history, prev_state):
            container = params[GENERATOR_CONTAINER_PARAM_KEY]
            generators = [
                container.get(generator_class)
                for generator_class in selector
            ]
            return policy_update_func(params, subset, state_history, prev_state, *generators)
        return decor
    return decorator
