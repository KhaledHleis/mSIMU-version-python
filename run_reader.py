import argparse

from backend.simulation.reader import Reader

from backend.utilities.utilities_json_reader import *

def main(filename):
    reader = Reader(filename=filename)
    reader.save_to_csv()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert JSON log files to CSV')
    parser.add_argument('filename', type=str, help='Path to the JSON file to convert')
    args = parser.parse_args()
    
    main(args.filename)