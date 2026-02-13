def get_string_key(key: str, json_data):
    return [item[key] for item in json_data]


def get_sensor_of_name(name: str, json_data):
    return [
        sensor
        for sensor_list in json_data
        for sensor in sensor_list
        if sensor["name"] == name
    ]
