"""
RNGProvider acts as a global source of random number generators
that combine a global entropy with a context thus ensuring
a level of consistency in the random numbers as the structure
of the simulation changes.
"""

import hashlib
import logging
from typing import List, Union
import numpy as np
# from model.constants import global_rng_entropy

class RNGProvider():
    """
    RNGProvider providers randum number generators based
    on a global entropy and contexts
    """
    seed: int
    monte_carlo_run: int

    def __init__(self, seed: int, monte_carlo_run: int):
        self.seed = seed
        self.monte_carlo_run = monte_carlo_run

    def get_rng(self, *context: List[Union[str, int]]) -> np.random.Generator:
        return np.random.default_rng(self.__seed__(list(context)))

    def __seed__(self, context: List[Union[str, int]]) -> np.random.SeedSequence:
        seed_sequence = np.random.SeedSequence(
            self.seed,
            spawn_key=map(abs, map(__hash__, [self.monte_carlo_run] + context))
        )
        logging.debug("Generated seed_sequence %s for context %s", seed_sequence, context)
        return seed_sequence

def __hash__(val: Union[str, int]) -> int:
    hex_hash = hashlib.md5(str(val).encode()).hexdigest()[0:16]
    return int(hex_hash, base=16)
