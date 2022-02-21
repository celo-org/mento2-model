<<<<<<< HEAD
import functools

from typing import Callable, List, Dict, Optional, Type
from radcad.wrappers import Context, Simulation
from radcad.core import generate_parameter_sweep

from . import Generator

=======
'''
GeneratorContainer manages the lifecycle of generators running in
the context of a simulation. It ensures generators are initialized
with the right parameters based on the parameter sweep happening
inside radcad and provides a useful decorator to inject them
into policy functions
'''
import functools

from typing import Callable, List, Dict, Type, Any
from radcad.wrappers import Context, Simulation
from radcad.core import generate_parameter_sweep

from .generator import Generator
>>>>>>> origin/master

class GeneratorContainer():
    '''
    The GeneratorContainer used as a singleton
    to manage the lifetimes of generators
    '''

    # Keeps a map of subset -> generator_class_name -> generator_instance
    generators_for_subset: Dict[str, Dict[str, Generator]] = {}

    def hook_to_simulation(self, simulation: Simulation, generator_classes: List[Type[Generator]]):
        '''
<<<<<<< HEAD
        Function is used to hook generators to a simulation by registering 

        '''
        simulation.before_subset = self.__hook__(
            self.__register_generators__(generator_classes),
            simulation.before_subset)

        simulation.after_run = self.__hook__(
            self.__clean__,
            simulation.after_run)
=======
        Register hooks on a simulation that help manage the lifetimes of
        generators for each subset run.
        '''
        __hook__(simulation, 'before_subset', self.__register_generators__(generator_classes))
        __hook__(simulation, 'after_run', self.__clean__)
>>>>>>> origin/master

    def inject(self, *selector: List[Generator]):
        '''
        Used to wrap policy functions in order to inject generators as arguments, e.g:

        @container.inject(SomeGenerator, SomeOtherGenerator)
<<<<<<< HEAD
        def p_update_policy(params, subset, state_history, prev_state, some_generator, some_other_generator):
            # do things with the generators
            pass
        '''
        def decorator(f):
            @functools.wraps(f)
=======
        def p_update_policy(params, subset, state_history, prev_state,
                            some_generator, some_other_generator):
            # do things with the generators
            pass
        '''
        def decorator(policy_update_func):
            @functools.wraps(policy_update_func)
>>>>>>> origin/master
            def decor(params, subset, state_history, prev_state):
                generators = [
                    self.__get_generator__(prev_state['__subset_id__'], generator_class)
                    for generator_class in selector
                ]
<<<<<<< HEAD
                return f(params, subset, state_history, prev_state, *generators)
=======
                return policy_update_func(params, subset, state_history, prev_state, *generators)
>>>>>>> origin/master
            return decor
        return decorator

    def __get_generator__(self, subset_id, generator_class):
        '''
<<<<<<< HEAD
        Try to lookup a generator for a subset
=======
        Get a generator by subset_id and class with helpful errors
>>>>>>> origin/master
        '''
        if self.generators_for_subset.get(subset_id) is None:
            raise RuntimeError(f"Generators not registered for subset {subset_id}")
        if self.generators_for_subset[subset_id].get(generator_class.__name__) is None:
            raise RuntimeError(
                f"Generator {generator_class.__name__} not registered for subset {subset_id}")

        return self.generators_for_subset[subset_id][generator_class.__name__]

    def __register_generators__(self, generator_classes: List[Generator]):
        '''
        Start generators before each subset of the simulation starts
        and register them in the container.
<<<<<<< HEAD
=======
        This is implemented as higherlevel function because it depends
        on the list of generators passed at hook time.
>>>>>>> origin/master
        '''
        def before_subset_hook(context: Context = None):
            param_sweep = generate_parameter_sweep(context.parameters)
            params = param_sweep[context.subset]
<<<<<<< HEAD
            subset_id = self.__subset_id__(context)
=======
            subset_id = __subset_id__(context)
>>>>>>> origin/master

            self.generators_for_subset[subset_id] = {
                generator.__class__.__name__: generator for generator in [
                    generator_class.from_parameters(params)
                    for generator_class in generator_classes
                ]
            }

            context.initial_state.update({'__subset_id__': subset_id})
        return before_subset_hook

<<<<<<< HEAD
    def __subset_id__(self, context: Context):
        return f"{context.simulation}:{context.run}:{context.subset}"

    def __hook__(self, hook: Callable, existing_hook: Optional[Callable]):
        '''
        Register a hook that wraps an existing hook if it's present
        '''
        if existing_hook:
            def _hook():
                existing_hook()
                hook()
            return _hook
        else:
            return hook

    def __clean__(self, context: Context):
        self.generators_for_subset = {}


=======
    def __clean__(self, _context: Context):
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
>>>>>>> origin/master
container = GeneratorContainer()
