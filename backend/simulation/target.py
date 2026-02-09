from backend.metaclasses.simu_class import SIMU
from abc import abstractmethod

import numpy as np

class Target(SIMU):
    
    @abstractmethod
    def calculate_field_at_position(self,position:np.ndarray)->np.ndarray:
        """
        
        An instance function for the target class that calculates the magnetic field vector from a point position in 3D space

        Args:
            position (np.ndarray): absolute sensor position

        Returns:
            np.ndarray: magnetic field vector or shape (1,3)
        """
        pass