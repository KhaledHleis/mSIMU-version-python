import pandas as pd
import numpy as np
from utilities.utilities_importer import *


class Trajectory_parser:

    @classmethod
    def read_pbp(cls, filename,ref:np.ndarray=None) -> tuple[float, np.ndarray, np.ndarray, np.ndarray]:
        """
        Read a trajectory point-by-point from a CSV file yield from the real experiment.
        if reference is provided the returned values will be cartesian coordinates relative to the reference point.

        Parameters
        ----------
        cls :
            Class reference (classmethod).
        filename : str
            Path to the CSV file. The file must contain the columns:
            "timestamp", "longitude", "latitude", "heading".
        ref : np.ndarray (optional)
            is a refrence point of coordinates that have the shape (1,3)
        Returns
        -------
        tuple[float, np.ndarray, np.ndarray, np.ndarray]
            deta_timestamp : float
                Difference between the first two timestamps (same units as the timestamp column).
            longitude : np.ndarray
                Longitude values from the CSV.
            latitude : np.ndarray
                Latitude values from the CSV.
            heading : np.ndarray
                Heading values from the CSV.
        """
        df_trajectory = pd.read_csv(filename)
        timestamps = np.array(df_trajectory["timestamp"])
        longitude = np.array(df_trajectory["longitude"])
        latitude = np.array(df_trajectory["latitude"])
        heading = np.array(df_trajectory["heading"])

        deta_timestamp = timestamps[1] - timestamps[0]

        if(ref!=None):
            coordinates = np.array([longitude,latitude,np.zeros_like(longitude)]).reshape((-1,3))
            coordinates = LLD_to_Coo(coordinates,ref)
            longitude = coordinates[0]
            latitude = coordinates[1]
        
        return deta_timestamp, longitude, latitude, heading
