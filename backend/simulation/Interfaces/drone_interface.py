from typing import List
import numpy as np
from backend.simulation.Interfaces.sensor_interface import ISensor
from backend.simulation.Interfaces.world_interface import IWorld
from backend.simulation.simu_objects.clock import Clock
class IDrone():
    name: str
    world: IWorld
    sensor_array: List[ISensor]
    current_position: np.ndarray
    current_rotation: np.ndarray # euler angles in radians, order: roll, pitch, yaw
    clock:Clock
    
    def update_current_data(self):
        pass
    def update_position(self,long,lat,rotation,depth = None):
        pass
    def __init__(self):
        pass