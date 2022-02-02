from abc import ABC, abstractmethod, abstractclassmethod
 
class Generator(ABC):
    @abstractclassmethod
    def from_parameters(cls, params) -> "Generator":
        pass

    @abstractmethod
    def next_state(self, prev_state):
        pass