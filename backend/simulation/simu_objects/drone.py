from typing import List
import numpy as np
from backend.metaclasses.simu_class import SIMU
from backend.simulation.simu_objects.world import World

from backend.simulation.Interfaces.sensor_interface import ISensor
from backend.simulation.Interfaces.drone_interface import IDrone
from backend.simulation.Interfaces.world_interface import IWorld
from backend.simulation.simu_objects.clock import Clock

from backend.utilities.utilities_converter import lld_to_ned

class Drone(SIMU,IDrone):
    name: str
    sensor_array: List[ISensor]
    current_position: np.ndarray
    current_rotation: np.ndarray
    clock: Clock
    world: IWorld

    def update_current_data(self):
        for sensor in self.sensor_array:
            c = sensor.make_measurement(self)

    def update_position(self, long, lat, rotation, depth=None):
        self.current_rotation = rotation
        self.current_position = lld_to_ned( np.array(
            [[long, lat, self.current_position[0, 2] if depth is None else depth]]
        ),self.world.reference_point)

    def __init__(self, name,sensor_array: List[ISensor],world: IWorld):
        super().__init__(name)
        self.sensor_array = sensor_array
        self.clock = Clock()
        self.world = world
