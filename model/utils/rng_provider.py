"""
RNGProvider acts as a global source of random number generators
that combine a global entropy with a context thus ensuring
a level of consistency in the random numbers as the structure
of the simulation changes.
"""

from typing import List, Union
import numpy as np
from model.constants import global_rng_entropy

class RNGProvider():
    """
    RNGProvider providers randum number generators based
    on a global entropy and contexts
    """
    entropy: int

    def __init__(self, entropy: int):
        self.entropy = entropy

    def get_rng(self, *context: List[Union[str, int]]) -> np.random.Generator:
        return np.random.default_rng(self.__seed__(context))

    def __seed__(self, context: List[Union[str, int]]) -> np.random.SeedSequence:
        return np.random.SeedSequence(
            self.entropy,
            spawn_key=map(abs, map(hash, context))
        )

rngp = RNGProvider(global_rng_entropy)
