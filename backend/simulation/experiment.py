from backend.simulation.Interfaces.drone_interface import IDrone
from backend.simulation.Interfaces.world_interface import IWorld
from backend.simulation.clock import Clock

from backend.simulation.parsers.trajectory_parser import TrajectoryParser
from backend.simulation.parsers.world_parser import WorldParser
from backend.simulation.parsers.drone_parser import DroneParser

from backend.utilities.utilities_logger import initialize_loggers_batch_with_timestamp


class experiment:

    def experiment_from_manip(self, world_file, trajectory_file, drone_file):
        world = WorldParser.Parse(world_file)
        drone = DroneParser.Parse(drone_file)
        delta_timestamp, longitude, latitude, heading = TrajectoryParser.read_pbp(
            trajectory_file, ref=world.reference_point
        )
        return delta_timestamp, longitude, latitude, heading, world, drone

    def run(self,experiment_name):
        delta_timestamp, longitude_array, latitude_array, heading_array, world, drone = self.experiment_from_manip()
        #! activate the clock 
        clock = Clock()
        clock.set_conversion_factor(delta_timestamp)
        drone.update_position(longitude,latitude,heading,depth = 0)
        drone_logger, world_logger, experiment_name = initialize_loggers_batch_with_timestamp(experiment_name)
        for longitude, latitude, heading in zip(longitude_array, latitude_array, heading_array):
            drone.update_position(longitude,latitude,heading)
            clock.increment_time()
            world_logger.log(world)
            drone_logger.log(drone)

    def __init__(self):
        pass
