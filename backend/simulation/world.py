import numpy as np
from typing import List
from backend.metaclasses.simu_class import SIMU
from backend.simulation.target import Target
class World(SIMU):    
    name:str
    reference_point:np.ndarray
    simulation_radius:int
    regional_magnetic_field:np.ndarray
    target_array:List[Target]
    
    def __init__(self,name,target_array):
        self.target_array = target_array #array of all targets in the simulation
        self.name = name

