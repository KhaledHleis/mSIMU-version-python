from typing import List
import numpy as np
from backend.simulation.Interfaces.sensor_interface import ISensor
from backend.simulation.Interfaces.drone_interface import IDrone
from backend.simulation.Interfaces.world_interface import IWorld
from backend.simulation.clock import Clock
class IDrone():
    name: str
    world: IWorld
    sensor_array: List[ISensor]
    current_position: np.ndarray
    current_heading: np.ndarray
    clock:Clock
    
    def __init__(self):
        pass