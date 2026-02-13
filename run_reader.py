from backend.utilities.utilities_importer import load_all_objects
import os 

from backend.utilities.utilities_json_reader import *

def main():
    directory = "logs/bb_59_20260213_111431"
    directory = os.path.join(directory,"drone")
    json_data = load_all_objects(directory)    
        
    sensor_array_data = get_string_key("sensor_array",json_data)
    sensor_1_data = get_sensor_of_name("sensor_UNO",sensor_array_data)
    
    import numpy as np
    magnetic_field = np.array(get_string_key("magnetic_field",sensor_1_data)).reshape(-1,3)
    
    import matplotlib.pyplot as plt
    plt.plot(magnetic_field)
    plt.show()

if __name__ == "__main__":
    main()