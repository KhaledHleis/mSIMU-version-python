import numpy as np

from pydantic import BaseModel
from typing import List, Optional
import json

from backend.simulation.simu_objects.world import World
from backend.simulation.simu_objects.target import Target
from backend.simulation.simu_objects.target import Cable
from backend.simulation.simu_objects.target import Dipole

from backend.utilities.utilities_importer import LLD_to_Coo


class WorldParser:
    @classmethod
    def __fff(cls, fake_class: BaseModel):
        """
        fill from fake, this method uses the fakeclass that is automaticaly populated using pydinamic to fill the actual class.
        """

        reference_point = np.array(
            [[fake_class.reference_longitude, fake_class.reference_latitude, 0]]
        )

        target_array: List[Target] = []
        for cable in fake_class.cables:
            start = np.array(
                [
                    cable.starting_longitude,
                    cable.starting_latitude,
                    cable.starting_depth,
                ]
            ).reshape(1, 3)
            end = np.array(
                [cable.ending_longitude, cable.ending_latitude, cable.ending_depth]
            ).reshape(1, 3)
            start = LLD_to_Coo(start, reference_point)
            end = LLD_to_Coo(end, reference_point)
            c = Cable(cable.name, start, end, cable.current)
            target_array.append(c)
        for dipole in fake_class.dipoles:
            center_point = np.array(
                [
                    dipole.center_longitude,
                    dipole.center_latitude,
                    dipole.center_depth,
                ]
            ).reshape(1, 3)
            center_point = LLD_to_Coo(center_point, reference_point)
            d = Dipole(dipole.name, center_point, dipole.dipole_moment)
            target_array.append(d)

        world = World(fake_class.name, target_array)
        world.reference_point = reference_point
        world.simulation_radius = fake_class.simulation_radius
        world.regional_magnetic_field = np.array(fake_class.regional_magnetic_field)
        return world

    @classmethod
    def Parse(cls, filename) -> World:
        """
        Parse a JSON file and convert it into a World instance.

        This classmethod opens the file at the provided path, parses its JSON
        content into a dictionary, constructs a FakeWorld using that dictionary,
        and then delegates construction of the final World object to the private
        class helper cls.__fff.

        Parameters
        ----------
        filename : str | os.PathLike
            Path to a JSON file containing a mapping of values accepted by
            FakeWorld's constructor.

        Returns
        -------
        World
            A World instance produced by calling cls.__fff on the parsed
            FakeWorld.

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
            for FakeWorld or if cls.__fff raises these on construction.

        Notes
        -----
        - The file is opened with the default system encoding.
        - The method expects the JSON top-level value to be an object (dict)
          whose keys and values match the parameters accepted by FakeWorld(**data).
        """
        with open(filename) as f:
            data = json.load(f)
        return cls.__fff(FakeWorld(**data))


#! these are template classes used to easily populate the classes from the json files
class FakeCable(BaseModel):
    name: str
    starting_longitude: float
    starting_latitude: float
    starting_depth: float
    ending_longitude: float
    ending_latitude: float
    ending_depth: float
    current: float


class FakeDipole(BaseModel):
    name: str
    center_longitude: float
    center_latitude: float
    center_depth: float
    dipole_moment: List[float]


class FakeWorld(BaseModel):
    name: str
    reference_longitude: float
    reference_latitude: float
    simulation_radius: int
    regional_magnetic_field: List[float]
    cables: Optional[List["FakeCable"]] = []
    dipoles: Optional[List["FakeDipole"]] = []
