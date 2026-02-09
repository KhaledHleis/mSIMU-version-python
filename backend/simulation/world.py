import numpy as np

from backend.metaclasses.simu_class import SIMU
from backend.simulation.target import Target
class World(SIMU):    
    
    def __init__(self,name,target_array):
        self.target_array = target_array #array of all targets in the simulation
        self.name = name

