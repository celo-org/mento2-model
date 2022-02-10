'''
Example policy function that showcases how Generators
can be injected into policy functions.
'''

from model.generators.container import container
from model.generators.example import ExampleGenerator

@container.inject(ExampleGenerator)
def p_bucket_update(_params, _substep, _state_history, _prev_state,
                    example_generator: ExampleGenerator):
    return {'example_state': example_generator.get_some_value()}
