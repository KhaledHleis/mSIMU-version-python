import numpy as np

from backend.simulation.target import Target

class Dipole(Target):
    
    def calculate_field_at_position(self, position) -> np.ndarray:
        position = np.asarray(position, dtype=float)

        R = position - self.center_point
        r = np.linalg.norm(R)

        if r == 0.0:
            raise ValueError("Field is undefined at the dipole center")

        R_hat = R / r
        m = self.dipole_moment

        field = (3.0 * np.dot(m, R_hat) * R_hat - m) / (r ** 3)
        return field

    def __init__(self, name:str, center_point:np.ndarray,dipole_moment:np.ndarray):
        self.name = name
        self.center_point = center_point
        self.dipole_moment = dipole_moment