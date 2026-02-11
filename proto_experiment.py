import matplotlib.pyplot as plt
import numpy as np

from backend.simulation.parsers.world_parser import WorldParser
from backend.simulation.parsers.trajectory_parser import Trajectory_parser

from backend.simulation.drone import Drone
from backend.simulation.world import World
from backend.simulation.sensor import Fluxgate


def main():
    #! prototype experiment to import trajectories and plot signal
    world_filename = "experiments/worlds/world_test1.json"
    world = WorldParser.Parse(world_filename)
    delta_timestamp, longitude, latitude, heading = Trajectory_parser.read_pbp(
        "experiments/real_trajectories/ellipse_19_Jan_2026_16-37-59.csv",
        world.reference_point,
    )
    heading = np.radians(heading)
    drone = Drone("Drone zero")
    sens = Fluxgate("sensor 0", drone, np.array([0, 0, 0]))
    drone.sensor_array = [sens]
    drone.world = world

    print(world)

    measurement = plot_measurement(longitude, latitude, heading, drone)
    plot_trajectory(longitude, latitude, measurement, world)


def plot_measurement(longitude, latitude, heading, drone):
    # longitude, latitude are already in NED: [North, East, Down]
    points = np.column_stack([longitude, latitude, np.zeros_like(latitude)])

    measurement = []
    for pos, head in zip(points, heading):
        drone.current_position = pos
        drone.current_heading = head
        measurement.append(drone.get_current_data())
    measurement = np.array(measurement).reshape((-1, 3))

    plt.figure()
    plt.plot(measurement, label=["Bx (forward)", "By (right)", "Bz (down)"])
    # plt.plot(heading/max(heading)*max(measurement[:,0]),label="Heading")
    plt.legend()
    plt.xlabel("Sample")
    plt.ylabel("Magnetic Field (nT)")
    plt.title("Magnetic Field Components in Body Frame")
    plt.show(block=False)

    plt.figure()
    norm_m = np.linalg.norm(measurement, axis=-1)
    plt.plot(norm_m)
    plt.ylim((min(norm_m), max(norm_m)))
    plt.xlabel("Sample")
    plt.ylabel("|B| (nT)")
    plt.title("Magnetic Field Magnitude")
    plt.show(block=False)

    return measurement


def plot_trajectory(longitude, latitude, measurement, world):
    # longitude = North, latitude = East in NED coordinates
    # For proper map display: x-axis = East, y-axis = North
    measurement_norm = np.linalg.norm(measurement, axis=-1)

    plt.figure()
    # Plot with East on x-axis, North on y-axis
    plt.scatter(latitude, longitude, c=measurement_norm, cmap="viridis")
    plt.colorbar(label="Bz (nT)")

    # Plot all cables in the target array
    for i, target in enumerate(world.target_array):
        # Extract cable endpoints in NED [North, East, Down]
        cable_north = [target.start_point[0, 0], target.end_point[0, 0]]
        cable_east = [target.start_point[0, 1], target.end_point[0, 1]]

        # Plot cable with East on x-axis, North on y-axis
        label = f"Cable {i}" if len(world.target_array) > 1 else "Cable"
        plt.plot(cable_east, cable_north, "-", linewidth=2, label=label)

    plt.xlabel("East (m)")
    plt.ylabel("North (m)")
    plt.title("Trajectory and Magnetic Field Magnitude")
    plt.legend()
    plt.axis("equal")
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    main()
