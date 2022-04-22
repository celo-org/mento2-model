'''
Example policy function that showcases how Generators
can be injected into policy functions.
'''

from lib.generator_container import inject
from model.generators.example import ExampleGenerator

@inject(ExampleGenerator)
def p_bucket_update(_params, _substep, _state_history, _prev_state,
                    example_generator: ExampleGenerator):
    return {'example_state': example_generator.get_some_value()}
