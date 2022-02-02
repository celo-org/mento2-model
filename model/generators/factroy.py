import re
from typing import List, Type, Dict, Any
from radcad.wrappers import Context, Model
from radcad.core import generate_parameter_sweep
from model.generators import Generator

class GeneratorFactory:
    components: List[Type[Generator]]

    def __init__(self, components: List[Type[Generator]]=[]):
        self.components = components

    def before_subset(self, context: Context = None):
        param_sweep = generate_parameter_sweep(context.parameters)
        params = param_sweep[context.subset]
        print(params)
        context.initial_state.update(self.__setup_components__(params))
    
    def __setup_components__(self, params):
        components_dict = {}
        for component in self.components:
            # MarketPriceGenerator => _market_price_generator
            component_name = re.sub('([A-Z]+)', r'_\1', component.__name__).lower() 
            component_instance = component.from_parameters(params)
            components_dict[component_name] = component_instance
        return components_dict