import pandas as pd
import os
import numpy as np

from backend.utilities.utilities_json_reader import *
from backend.utilities.utilities_exporter import COO_to_LLD

class Reader:

    json_object: object

    def save_to_csv(self, sensor_name="sensor_UNO", gradiometer=False):
        #! get from json object
        clock_array = get_string_key("clock", self.json_object)
        time_stamp = np.array(
            get_string_key("_Clock__time_stamp", clock_array)
        ).reshape(-1)

        position_array = np.array(
            get_string_key("current_position", self.json_object)
        ).reshape(-1, 3)

        heading_array = np.array(
            get_string_key("current_rotation", self.json_object)
        ).reshape(-1)[-1]

        sensor_array_data = get_string_key("sensor_array", self.json_object)

        # Normalize sensor_name to a list
        if isinstance(sensor_name, str):
            sensor_names = [sensor_name]
        else:
            sensor_names = list(sensor_name)

        multi = len(sensor_names) > 1

        # Validate gradiometer usage
        if gradiometer and len(sensor_names) != 2:
            raise ValueError("Gradiometer mode requires exactly 2 sensor names.")

        #! convert to data frame
        df = pd.DataFrame()

        df["timestamp"] = time_stamp

        # Convert NE to LLD
        LLD = COO_to_LLD(
            position_array,
            np.array(self.json_object[0]["world"]["reference_point"])
        )
        df["longitude"] = LLD[:, 0]
        df["latitude"]  = LLD[:, 1]
        df["ve"]        = np.zeros_like(time_stamp)
        df["vn"]        = np.zeros_like(time_stamp)
        df["vd"]        = np.zeros_like(time_stamp)
        df["heading"]   = heading_array

        # Read magnetic field for each sensor
        mag_fields = []
        for name in sensor_names:
            sensor_data  = get_sensor_of_name(name, sensor_array_data)
            mag_field    = np.array(
                get_string_key("measurement", sensor_data)
            ).reshape(-1, 3)
            mag_fields.append(mag_field)

        if gradiometer:
            # Difference between the two sensors — same column names as single-sensor case
            mag_fields = [mag_fields[0] - mag_fields[1]]
            sensor_names = [None]   # sentinel: use default column names
            multi = False

        for mag_field, name in zip(mag_fields, sensor_names):
            suffix = f"_{name}" if multi else ""
            df[f"magx{suffix}"] = mag_field[:, 0]
            df[f"magy{suffix}"] = mag_field[:, 1]
            df[f"magz{suffix}"] = mag_field[:, 2]
            df[f"mag{suffix}"]  = np.linalg.norm(mag_field, axis=-1)

        df.to_csv(os.path.join(self.directory_base, f"manip{'_gradio' if gradiometer else ''}.csv"), index=False)

    def __init__(self, filename):
        self.directory_base = filename
        directory = os.path.join(filename, "drone")
        self.json_object = load_all_objects(directory)