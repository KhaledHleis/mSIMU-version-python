import numpy as np
from abc import abstractmethod
class ISensor():
    name: str
    relative_position: np.ndarray
    magnetic_field:np.ndarray
    
    @abstractmethod
    def make_measurement(self):
        pass
    
    def __init__(self):
        pass