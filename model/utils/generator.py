'''
The abstract Generator Class
'''
import logging
from abc import ABC, abstractmethod
from typing import Callable, Dict, Optional

def state_update_blocks(selector: str) -> Callable:
    """
    Decorator used in Generators to specify that a method is meant
    to return state update blocks for a given selector.
    """
    def decorator(method):
        method.__is_state_update_block_provider__ = True
        method.__state_update_blocks_selector__ = selector
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

    __state_update_blocks__: Dict[str, Callable] = {}
    __state_update_blocks_cached__ = False

    @classmethod
    @abstractmethod
    def from_parameters(cls, params) -> "Generator":
        pass

    def state_update_blocks(self, selectors: Optional[str]):
        """
        Either inject all state update blocks for a generator or
        matched based on the provided selectors
        """
        if self.__state_update_blocks_cached__ is False:
            self.__create_state_update_blocks_cache__()

        state_update_blocks_to_inject = []
        if not selectors:
            state_update_blocks_to_inject = self.__state_update_blocks__.values()
        else:
            for selector in selectors:
                selector_blocks_builder = self.__state_update_blocks__.get(selector, None)
                if selector_blocks_builder is None:
                    logging.warning(
                        "No state_update_blocks for %s with selector:%s",
                        self.__class__.__name__,
                        selector
                    )
                else:
                    state_update_blocks_to_inject.append(selector_blocks_builder)

        return [
            state_update_block
            for selector_blocks in map(lambda x: x(), state_update_blocks_to_inject)
            for state_update_block in selector_blocks
        ]

    def __create_state_update_blocks_cache__(self):
        """
        On the first run this analyzes the methods in the object
        to create a cache of selector -> method for state_update_block providers.
        """
        for method_name in dir(self):
            method = getattr(self, method_name)
            is_provider = callable(method) and \
                          getattr(method, '__is_state_update_block_provider__', False)
            if is_provider:
                selector = method.__state_update_blocks_selector__
                self.__state_update_blocks__[selector] = method
