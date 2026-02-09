from backend.simulation.parsers.world_parser import WorldParser
from backend.simulation.parsers.trajectory_parser import Trajectory_parser
def main():
    #! prototype experiment to import trajectories and plot them in world
    world_filename = "experiments/worlds/world_test1.json"
    world = WorldParser.Parse(world_filename)
    delta_timestamp, longitude, latitude, heading = Trajectory_parser.read_pbp("experiments/real_trajectories/ellipse_19_Jan_2026_16-28-27.csv",world.reference_point)
    
    print(world.reference_point, longitude.shape,longitude,latitude)
    
    import matplotlib.pyplot as plt
    import numpy as np
    points = np.array([longitude,latitude]).reshape(-1,2)
    
    plt.title(f"{points.shape[0]} points have been plotted a dt is {delta_timestamp}")
    plt.scatter(longitude,latitude)
    plt.scatter(world.reference_point[:,0],world.reference_point[:,1])
    plt.show()
    
if __name__ == "__main__":
    main()