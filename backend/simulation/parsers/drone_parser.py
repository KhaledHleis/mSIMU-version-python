import numpy as np
from pydantic import BaseModel
from typing import List, Optional
import json

from backend.simulation.drone import Drone
from backend.simulation.sensor import Fluxgate
from backend.simulation.Interfaces.drone_interface import IDrone
from backend.simulation.Interfaces.sensor_interface import ISensor


class DroneParser:
    @classmethod
    def __fff(cls, fake_drone: BaseModel, world) -> IDrone:
        """
        Fill from fake, this method uses the fake class that is automatically 
        populated using pydantic to fill the actual class.
        """
        # Create the drone instance
        drone = Drone(fake_drone.name)
        drone.world = world
        
        # Initialize sensor array
        sensor_array: List[ISensor] = []
        
        for fake_sensor in fake_drone.sensors:
            relative_position = np.array(fake_sensor.relative_position).reshape(1, 3)
            
            # Create sensor based on type
            if fake_sensor.type == "Fluxgate":
                sensor = Fluxgate(
                    fake_sensor.name,
                    drone,
                    relative_position
                )
            # Add more sensor types here as needed
            # elif fake_sensor.type == "OtherSensorType":
            #     sensor = OtherSensor(...)
            else:
                raise ValueError(f"Unknown sensor type: {fake_sensor.type}")
            
            sensor_array.append(sensor)
        
        drone.sensor_array = sensor_array
        
        # Initialize position and heading (can be set later via update_position)
        drone.current_position = np.array([[0, 0, 0]])
        drone.current_heading = 0
        
        return drone

    @classmethod
    def Parse(cls, filename, world) -> IDrone:
        """
        Parse a JSON file and convert it into a Drone instance.

        This classmethod opens the file at the provided path, parses its JSON
        content into a dictionary, constructs a FakeDrone using that dictionary,
        and then delegates construction of the final Drone object to the private
        class helper cls.__fff.

        Parameters
        ----------
        filename : str | os.PathLike
            Path to a JSON file containing a mapping of values accepted by
            FakeDrone's constructor.
        world : IWorld
            The World instance that this drone will operate in.

        Returns
        -------
        IDrone
            A Drone instance produced by calling cls.__fff on the parsed
            FakeDrone.

        Raises
        ------
        FileNotFoundError
            If the file does not exist.
        OSError
            For other I/O related errors while opening or reading the file.
        json.JSONDecodeError
            If the file does not contain valid JSON.
        TypeError, ValueError
            If the parsed JSON does not have the expected structure or types
            for FakeDrone or if cls.__fff raises these on construction.

        Notes
        -----
        - The file is opened with the default system encoding.
        - The method expects the JSON top-level value to be an object (dict)
          whose keys and values match the parameters accepted by FakeDrone(**data).
        """
        with open(filename) as f:
            data = json.load(f)
        return cls.__fff(FakeDrone(**data), world)


#! These are template classes used to easily populate the classes from the json files
class FakeSensor(BaseModel):
    name: str
    relative_position: List[float]
    type: str


class FakeDrone(BaseModel):
    name: str
    sensors: Optional[List[FakeSensor]] = []