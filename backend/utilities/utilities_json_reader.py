def get_string_key(key: str, json_data):
    return [item[key] for item in json_data]


def get_sensor_of_name(name: str, json_data):
    return [
        sensor
        for sensor_list in json_data
        for sensor in sensor_list
        if sensor["name"] == name
    ]


def load_all_objects(directory):
    import json
    from pathlib import Path

    """Load all objects from all JSON files into a single list"""
    all_objects = []
    
    for json_file in Path(directory).glob('*.json'):
        with open(json_file, 'r') as f:
            objects = json.load(f)
            all_objects.extend(objects)  # Add all objects from this file
    
    return all_objects