'''
The abstract Generator Class
'''
from abc import ABC, abstractmethod


# pylint: disable=too-few-public-methods,no-self-use
class Generator(ABC):
    '''
    Abstract Generator class, this is very light at the moment
    but might grow if we discover patterns in Generators that
    are worth abstracting, either way having this is helpful
    for the type system.
    '''

    @classmethod
    @abstractmethod
    def from_parameters(cls, params) -> "Generator":
        pass

    def state_update_blocks(self):
        return []
