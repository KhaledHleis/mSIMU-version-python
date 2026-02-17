import pandas as pd
import os
import numpy as np

from backend.utilities.utilities_json_reader import *
from backend.utilities.utilities_exporter import COO_to_LLD

class Reader:

    json_object: object

    def save_to_csv(self):
        #! get from json object
        clock_array = get_string_key("clock", self.json_object)
        time_stamp = np.array(
            get_string_key("_Clock__time_stamp", clock_array)
        ).reshape(-1)

        position_array = np.array(
            get_string_key("current_position", self.json_object)
        ).reshape(-1, 3)

        heading_array = np.array(
            get_string_key("current_heading", self.json_object)
        ).reshape(-1)

        sensor_array_data = get_string_key("sensor_array", self.json_object)
        sensor_1_data = get_sensor_of_name("sensor_UNO", sensor_array_data)
        magnetic_field = np.array(
            get_string_key("magnetic_field", sensor_1_data)
        ).reshape(-1, 3)

        #! convert to data frame
        df = pd.DataFrame()

        df["timestamp"] = time_stamp
        #convert NE to LLD
        LLD = COO_to_LLD(position_array,np.array(self.json_object[0]["world"]["reference_point"]))
        df["longitude"] =  LLD[:, 0]
        df["latitude"] = LLD[:, 1]
        df["ve"] = np.zeros_like(time_stamp)
        df["vn"] = np.zeros_like(time_stamp)
        df["vd"] = np.zeros_like(time_stamp)
        df["heading"] = heading_array
        df["magx"] = magnetic_field[:, 0]
        df["magy"] = magnetic_field[:, 0]
        df["magz"] = magnetic_field[:, 0]
        df["mag"] = np.linalg.norm(magnetic_field, axis=-1)

        df.to_csv(os.path.join(self.directory_base, "manip.csv"), index=False)

    def __init__(self, filename):
        self.directory_base = filename
        directory = os.path.join(filename, "drone")
        self.json_object = load_all_objects(directory)
