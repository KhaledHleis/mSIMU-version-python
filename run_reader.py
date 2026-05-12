import argparse

from backend.simulation.reader import Reader

from backend.utilities.utilities_json_reader import *

def main(filename, gradiometer=False):
    reader = Reader(filename=filename)
    reader.save_to_csv(gradiometer=gradiometer)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert JSON log files to CSV')
    parser.add_argument('filename', type=str, help='Path to the JSON file to convert')
    parser.add_argument('--gradiometer', '-g', action='store_true', help='Indicates if the sensors are in gradiometer configuration (requires exactly 2 sensor names)')
    parser.add_argument('--sensor_names', '-s', nargs='+', help='List of sensor names to extract data for (default: all sensors)')
    args = parser.parse_args()
    
    main(args.filename, gradiometer=args.gradiometer)