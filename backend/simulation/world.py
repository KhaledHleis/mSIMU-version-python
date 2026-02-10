import numpy as np
from typing import List
from backend.metaclasses.simu_class import SIMU

from backend.simulation.Interfaces.target_interface import ITarget
from backend.simulation.Interfaces.world_interface import IWorld
class World(SIMU,IWorld):    
    name:str
    reference_point:np.ndarray
    simulation_radius:int
    regional_magnetic_field:np.ndarray
    target_array:List[ITarget]
    
    
    def calculate_entire_field_at_position(self,position:np.ndarray)->np.ndarray:
        B = self.regional_magnetic_field.copy().reshape(1,3)
        for target in self.target_array:
            B += target.calculate_field_at_position(position)
        return B
    
    def __init__(self,name,target_array):
        self.target_array = target_array #array of all targets in the simulation
        self.name = name

