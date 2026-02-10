from backend.simulation.parsers.world_parser import WorldParser
from backend.simulation.parsers.trajectory_parser import Trajectory_parser

from backend.simulation.drone import Drone
from backend.simulation.sensor import Fluxgate
def main():
    #! prototype experiment to import trajectories and plot signal
    world_filename = "experiments/worlds/world_test1.json"
    world = WorldParser.Parse(world_filename)
    delta_timestamp, longitude, latitude, heading = Trajectory_parser.read_pbp("experiments/real_trajectories/ellipse_19_Jan_2026_16-28-27.csv",world.reference_point)
    
    print(world.reference_point, longitude.shape,longitude,latitude)
    
    import matplotlib.pyplot as plt
    import numpy as np
    points = np.array([longitude,latitude,np.zeros_like(latitude)]).reshape(-1,3)
    
    drone = Drone("Drone zero")
    sens = Fluxgate("sensor 0",drone,np.array([0,0,0]))
    drone.sensor_array = [sens]
    drone.world = world
    mesurment = []
    for pos,head in zip(points,heading):
        drone.current_position = pos
        drone.current_heading = head
        mesurment.append(drone.get_current_data())
    plt.plot(mesurment)
    plt.show()
    
if __name__ == "__main__":
    main()