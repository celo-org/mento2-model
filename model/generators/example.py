'''
ExampleGenerator to showcase the generator pattern
'''
from .generator import Generator

class ExampleGenerator(Generator):
    '''
    The ExampleGenerator
    '''
    value: int = 42
    def __init__(self):
        pass

    @classmethod
    def from_parameters(cls, params) -> "ExampleGenerator":
        return cls()

    def get_some_value(self) -> int:
        return self.value
