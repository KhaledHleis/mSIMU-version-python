from typing import List
import numpy as np
from backend.metaclasses.simu_class import SIMU
from backend.simulation.world import World

from backend.simulation.Interfaces.sensor_interface import ISensor
from backend.simulation.Interfaces.drone_interface import IDrone

class Drone(SIMU,IDrone):
    name:str
    world:World
    sensor_array:List[ISensor]
    current_position:np.ndarray
    current_heading:np.ndarray
    
    #Hack: this is a place holder function, you should change it later ...
    def get_current_data(self):
        for sensor in self.sensor_array:
            c=sensor.make_mesurment()
        return c
    
    def __init__(self, name):
        super().__init__(name)