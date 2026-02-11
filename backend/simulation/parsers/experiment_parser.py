import numpy as np
from pydantic import BaseModel
from typing import Optional
import json

from backend.simulation.experiment import Experiment


class ExperimentParser:
    @classmethod
    def __fff(cls, fake_experiment: BaseModel) -> Experiment:
        """
        Fill from fake, this method uses the fake class that is automatically 
        populated using pydantic to fill the actual class.
        """
        # Create the experiment instance
        experiment = Experiment(fake_experiment.world_name)
        
        # Set basic parameters
        experiment.world_name = fake_experiment.world_name
        experiment.drone_name = fake_experiment.drone_name
        experiment.trajectory_type = fake_experiment.trajectory_type
        
        # Set trajectory-specific parameters based on type
        if fake_experiment.trajectory_type == "pp":
            if fake_experiment.pp_trajectory_filename:
                experiment.pp_trajectory_filename = fake_experiment.pp_trajectory_filename
            else:
                raise ValueError("trajectory_type 'pp' requires pp_trajectory_filename parameter")
        
        # Add more trajectory types here as needed
        # elif fake_experiment.trajectory_type == "circle":
        #     experiment.circle_radius = fake_experiment.circle_radius
        #     experiment.circle_center = fake_experiment.circle_center
        # elif fake_experiment.trajectory_type == "waypoint":
        #     experiment.waypoint_list = fake_experiment.waypoint_list
        
        return experiment

    @classmethod
    def Parse(cls, filename) -> Experiment:
        """
        Parse a JSON file and convert it into an Experiment instance.

        This classmethod opens the file at the provided path, parses its JSON
        content into a dictionary, constructs a FakeExperiment using that dictionary,
        and then delegates construction of the final Experiment object to the private
        class helper cls.__fff.

        Parameters
        ----------
        filename : str | os.PathLike
            Path to a JSON file containing a mapping of values accepted by
            FakeExperiment's constructor.

        Returns
        -------
        Experiment
            An Experiment instance produced by calling cls.__fff on the parsed
            FakeExperiment.

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
            for FakeExperiment or if cls.__fff raises these on construction.

        Notes
        -----
        - The file is opened with the default system encoding.
        - The method expects the JSON top-level value to be an object (dict)
          whose keys and values match the parameters accepted by FakeExperiment(**data).
        - World and Drone objects are NOT initialized by this parser; only their
          names are stored. The experiment should load/initialize these separately.
        """
        with open(filename) as f:
            data = json.load(f)
        return cls.__fff(FakeExperiment(**data))


#! These are template classes used to easily populate the classes from the json files
class FakeExperiment(BaseModel):
    world_name: str
    drone_name: str
    trajectory_type: str
    
    # Optional parameters for different trajectory types
    pp_trajectory_filename: Optional[str] = None
    
    # Placeholder for future trajectory types
    # circle_radius: Optional[float] = None
    # circle_center: Optional[List[float]] = None
    # waypoint_list: Optional[List[List[float]]] = None
    # lawnmower_width: Optional[float] = None
    # lawnmower_spacing: Optional[float] = None