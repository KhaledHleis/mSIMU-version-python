import numpy as np

from backend.simulation.target import Target

class Cable(Target):

    def __init__(
        self,
        name: str,
        start_point: np.ndarray,
        end_point: np.ndarray,
        current: float
    ):
        self.name = name
        self.start_point = np.asarray(start_point, dtype=float)
        self.end_point = np.asarray(end_point, dtype=float)
        self.current = current

    def calculate_field_at_position(self, position) -> np.ndarray:
        position = np.asarray(position, dtype=float)

        R1 = position - self.start_point
        R2 = position - self.end_point
        L = self.end_point - self.start_point

        r1 = np.linalg.norm(R1)
        r2 = np.linalg.norm(R2)

        cross_R1_R2 = np.cross(R1, R2)
        cross_norm_sq = np.dot(cross_R1_R2, cross_R1_R2)

        if cross_norm_sq == 0.0:
            raise ValueError("Field is undefined on the cable axis")

        term = (np.dot(R1, L) / r1) - (np.dot(R2, L) / r2)

        field = self.current * cross_R1_R2 / cross_norm_sq * term
        return field
