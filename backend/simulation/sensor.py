
#? python packages
import numpy as np
from abc import abstractmethod
#? abstract classes
from backend.metaclasses.simu_class import SIMU
#? utilities
from backend.utilities.utilities_converter import Absolute_position,convert_field_ned_to_body
#? interfaces
from backend.simulation.Interfaces.sensor_interface import ISensor
from backend.simulation.Interfaces.drone_interface import IDrone

class Sensor(SIMU,ISensor):
    name: str
    parent_drone:IDrone
    relative_position: np.ndarray

    @abstractmethod
    def make_measurement(self):
        pass

    def __init__(self, name, parent_drone: IDrone, relative_position: np.ndarray):
        super().__init__(name)
        self.parent_drone = parent_drone
        self.relative_position = relative_position


class Fluxgate(Sensor):

    def make_measurement(self):
        world = self.parent_drone.world
        
        # Get field in NED frame at sensor position
        field_ned = world.calculate_entire_field_at_position(
            Absolute_position(
                self.parent_drone.current_position, 
                self.parent_drone.current_heading,
                self.relative_position
            )
        )
        
        # Convert from NED to body frame using drone's attitude
        field_body = convert_field_ned_to_body(
            field_ned,
            0,
            0,
            self.parent_drone.current_heading  # yaw
        )
        
        return field_body
