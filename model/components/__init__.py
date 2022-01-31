from abc import ABC, abstractmethod, abstractclassmethod
 
class ModelComponent(ABC):
    @abstractclassmethod
    def from_parameters(cls, params) -> "ModelComponent":
        pass

    @abstractmethod
    def next_state(self, prev_state):
        pass