import functools

from typing import Callable, List, Dict, Optional, Type
from radcad.wrappers import Context, Simulation
from radcad.core import generate_parameter_sweep

from . import Generator

class GeneratorContainer():
    '''
    The GeneratorContainer used as a singleton
    to manage the lifetimes of generators
    '''

    # Keeps a map of subset -> generator_class_name -> generator_instance
    generators_for_subset: Dict[str, Dict[str, Generator]] = {}

    def hook_to_simulation(self, simulation: Simulation, generator_classes: List[Type[Generator]]):
        '''
        Function is used to hook generators to a simulation by registering 

        '''
        simulation.before_subset = self.__hook__(
            self.__register_generators__(generator_classes),
            simulation.before_subset)

        simulation.after_run = self.__hook__(
            self.__clean__,
            simulation.after_run)

    def inject(self, *selector: List[Generator]):
        '''
        Used to wrap policy functions in order to inject generators as arguments, e.g:

        @container.inject(SomeGenerator, SomeOtherGenerator)
        def p_update_policy(params, subset, state_history, prev_state, some_generator, some_other_generator):
            # do things with the generators
            pass
        '''
        def decorator(f):
            @functools.wraps(f)
            def decor(params, subset, state_history, prev_state):
                generators = [
                    self.__get_generator__(prev_state['__subset_id__'], generator_class)
                    for generator_class in selector
                ]
                return f(params, subset, state_history, prev_state, *generators)
            return decor
        return decorator

    def __get_generator__(self, subset_id, generator_class):
        '''
        Try to lookup a generator for a subset
        '''
        if self.generators_for_subset.get(subset_id) is None:
            raise RuntimeError(f"Generators not registered for subset {subset_id}")
        if self.generators_for_subset[subset_id].get(generator_class.__name__) is None:
            raise RuntimeError(f"Generator {generator_class.__name__} not registered for subset {subset_id}")

        return self.generators_for_subset[subset_id][generator_class.__name__]
    
    
    def __register_generators__(self, generator_classes: List[Generator]):
        '''
        Start generators before each subset of the simulation starts
        and register them in the container.
        '''
        def before_subset_hook(context: Context = None):
            param_sweep = generate_parameter_sweep(context.parameters)
            params = param_sweep[context.subset]
            subset_id = self.__subset_id__(context)

            self.generators_for_subset[subset_id] = {
                generator.__class__.__name__: generator for generator in [
                    generator_class.from_parameters(params) 
                    for generator_class in generator_classes
                ]
            }

            context.initial_state.update({'__subset_id__': subset_id})
        return before_subset_hook

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
                
    
container = GeneratorContainer()
