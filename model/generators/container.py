'''
GeneratorContainer manages the lifecycle of generators running in
the context of a simulation. It ensures generators are initialized
with the right parameters based on the parameter sweep happening
inside radcad and provides a useful decorator to inject them
into policy functions
'''
import functools

from typing import Callable, List, Dict, Any
from radcad.wrappers import Context, Simulation

from .generator import Generator

class GeneratorContainer():
    '''
    The GeneratorContainer used as a singleton
    to manage the lifetimes of generators
    '''

    # Keeps a map of subset -> generator_class_name -> generator_instance
    generators_for_subset: Dict[str, Dict[str, Generator]] = {}

    def hook_to_simulation(self, simulation: Simulation):
        '''
        Register hooks on a simulation that help manage the lifetimes of
        generators for each subset run.
        '''
        __hook__(simulation, 'before_subset', self.__set_subset_id__)
        __hook__(simulation, 'after_run', self.__clean__)

    def inject(self, *selector: List[Generator]):
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
                generators = [
                    self.__get_generator__(prev_state['__subset_id__'], generator_class, params)
                    for generator_class in selector
                ]
                return policy_update_func(params, subset, state_history, prev_state, *generators)
            return decor
        return decorator

    def __get_generator__(self, subset_id, generator_class, params):
        '''
        Get a generator by subset_id and class with helpful errors
        '''
        if self.generators_for_subset.get(subset_id) is None:
            self.generators_for_subset[subset_id] = {}
        if self.generators_for_subset[subset_id].get(generator_class.__name__) is None:
            self.generators_for_subset[subset_id][generator_class.__name__] = \
                generator_class.from_parameters(params)

        return self.generators_for_subset[subset_id][generator_class.__name__]

    @staticmethod
    def __set_subset_id__(context: Context = None):
        '''
        Sets the subset id in the initial state to be used later to
        segment generators.
        '''
        subset_id = __subset_id__(context)
        context.initial_state.update({'__subset_id__': subset_id})

    def __clean__(self, **_kwargs):
        '''
        Reset all generators at the end of a simulation.
        '''
        self.generators_for_subset = {}

def __hook__(simulation: Any, hook_name: str, hook: Callable):
    '''
    Sets a hook on a simulation but ensures that it gets
    nested if a hook is already defined
    '''
    existing_hook = getattr(simulation, hook_name)
    if existing_hook:
        def _hook():
            existing_hook()
            hook()
        setattr(simulation, hook_name, _hook)
    else:
        setattr(simulation, hook_name, hook)

def __subset_id__(context: Context):
    '''
    Generate a unique subset id from a radcad.Context
    '''
    return f"{context.simulation}:{context.run}:{context.subset}"

# Singleton container used throughout the lifetime of the execution
container = GeneratorContainer()
