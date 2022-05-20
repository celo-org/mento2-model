'''
The abstract Generator Class
'''
import logging
from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Type

def state_update_blocks(selector: str) -> Callable:
    """
    Decorator used in Generators to specify that a method is meant
    to return state update blocks for a given selector.
    """
    def decorator(method):
        method.__is_state_update_block_provider__ = True
        method.__state_update_block_provider_selector__ = selector
        return method
    return decorator

# pylint: disable=too-few-public-methods,no-self-use
class Generator(ABC):
    '''
    Abstract Generator class, this is very light at the moment
    but might grow if we discover patterns in Generators that
    are worth abstracting, either way having this is helpful
    for the type system.
    '''

    __state_update_block_providers__: Dict[str, Callable] = {}
    __state_update_block_providers_cached__ = False

    @classmethod
    @abstractmethod
    def from_parameters(cls, params, initial_state) -> "Generator":
        pass

    def state_update_blocks(self, selectors: List[str]):
        """
        Either inject all state update blocks for a generator or
        matched based on the provided selectors
        """
        if self.__state_update_block_providers_cached__ is False:
            self.__cache_state_update_block_providers__()

        state_update_block_providers = []
        if not selectors:
            state_update_block_providers = self.__state_update_block_providers__.values()
        else:
            for selector in selectors:
                provider = self.__state_update_block_providers__.get(selector, None)
                if provider is None:
                    logging.warning(
                        "No state_update_blocks for %s with selector:%s",
                        self.__class__.__name__,
                        selector
                    )
                else:
                    state_update_block_providers.append(provider)

        return [
            state_update_block
            for selector_blocks in [provider() for provider in state_update_block_providers]
            for state_update_block in selector_blocks
        ]

    def __cache_state_update_block_providers__(self):
        """
        On the first run this analyzes the methods in the object
        to create a cache of selector -> method for state_update_block providers.
        """
        for method_name in dir(self):
            method = getattr(self, method_name)
            is_provider = callable(method) and \
                          getattr(method, '__is_state_update_block_provider__', False)
            if is_provider:
                selector = method.__state_update_block_provider_selector__
                self.__state_update_block_providers__[selector] = method

def generator_state_update_block(generator_class: Type[Generator], *selectors: List[str]):
    """
    Returns a placeholder for one or more state update blocks which
    are dynamically inserted for each simulation run from the generator.
    These are processed by the model.utils.engine.Engine class.
    """
    return {
        'type': 'generator',
        'source': generator_class,
        'selectors': selectors
    }
