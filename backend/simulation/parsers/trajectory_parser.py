import pandas as pd
import numpy as np

from backend.utilities.utilities_converter import lld_to_ned_batch


class TrajectoryParser:

    @classmethod
    def read_pbp(cls, filename) -> tuple[float, np.ndarray, np.ndarray, np.ndarray]:
        df_trajectory = pd.read_csv(filename)
        timestamps = np.array(df_trajectory["timestamp"])
        longitude = np.array(df_trajectory["longitude"])
        latitude = np.array(df_trajectory["latitude"])
        heading = np.radians(np.array(df_trajectory["heading"]))

        delta_timestamp = timestamps[1] - timestamps[0]

        return delta_timestamp, longitude, latitude, heading
