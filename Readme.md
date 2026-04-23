# mSIMU-version-python

Python implementation of **mSIMU** — a modular simulation framework for modeling a moving drone equipped with magnetic sensors inside a virtual world containing magnetic targets such as **cables** and **dipoles**.

The system appears designed for **magnetic anomaly detection**, sensor simulation, and experiment replay using trajectory files.

***

# Features

* Drone simulation with dynamic movement

* Fluxgate magnetic sensor support

* Magnetic targets:

  * Cables

  * Dipoles

* JSON-based configuration files

* Replay point-by-point trajectories

* Logging system for simulation outputs

* Modular architecture for extending sensors and targets

***

# Project Structure

```bash
|   .gitignore
|   LICENSE
|   Readme.md
|   run_program.py  # Run the simulation from configuration file
|   run_reader.py   # Run a script to read and convert simulation logs
|   simulation004.drawio  # Class diagram drawing of the program open with "https://www.drawio.com/"
+---backend
|   +---metaclasses # Abstraction for classes involved in the simulation
|   +---simulation
|   |   +---Interfaces
|   |   +---loggers  # Advanced logging classes
|   |   +---parsers  # Classes used to populate simulation objects from configuration files
|   |   \---simu_objects  # Classes involved directly in the simulation     
|   \---utilities     # Methods used throughout the simulation and the program
\---examples
    +---drones
    +---experiment_config
    +---trajectories
    \---worlds
```

***

# Requirements

Install dependencies:

```bash
pip install numpy pydantic
```

You may also need:

```bash
pip install matplotlib pandas
```

(depending on utilities used later)

***

# How It Works

The simulation uses an **experiment JSON file** that defines:

* experiment name

* world file

* drone file

* trajectory type

* logging options

Then it:

1. Loads world targets
2. Loads drone + sensors
3. Loads trajectory path
4. Moves drone through trajectory points
5. Updates sensor readings
6. Logs outputs

***

# Running a Simulation

```bash
python run_program.py config.json
```

Example:

```bash
python run_program.py examples\experiment_config\bb_S90.json
```

***

# Example Experiment Config

```json
{
    "experiment_name":"bb_S90",
    "world_name":"examples/worlds/world_Cable_sud.json", # the filename linking to the world configuration
    "drone_name":"examples/drones/cyclope.json",  # the filename linking to the drone configuration
    "trajectory_type":"pp", # option for trajectory type pp is "point to point" uses a predefined trajectory points
    "pp_trajectory_filename":"examples/trajectories/waypoints_90deg.csv" # obligatory when using pp as trajectory type, a csv file containing the coordinates and heading
}
```

***

# World Configuration

Supports:

## Cable Target

```json
{
  "name": "Cable_south",
  "starting_longitude": -4.503827049110521,
  "starting_latitude": 48.492313209033945,
  "starting_depth": 1.5,
  "current": 6,
  "current_frequency": 0,
  "ending_longitude": -4.50434496199812,
  "ending_latitude": 48.49227909392259,
  "ending_depth": 1
}
```

## Dipole Target

```json
{
  "name": "Dipole_1",
  "center_longitude": -4.503827049110521,
  "center_latitude": 48.492313209033945,
  "center_depth": 8,
  "dipole_moment": [1, 0, 1]
}
```

***

# Drone Configuration

```json
{
  "name": "Drone_1",
  "sensors": [
    {
      "name": "Fluxgate_1",
      "relative_position": [0,0,0],
      "type": "Fluxgate"
    }
  ]
}
```

***

# Logging

Simulation outputs are automatically logged unless:

```json
"skip_logging": true
```

***

# Extending the Project

Easy to add:

* New sensor types

* New target types

* New trajectories

* Visualization dashboards

* Real-time streaming

***

# Main Entry Files

## Run Simulation

```bash
run_program.py
```

## Read Logs / Results

```bash
run_reader.py
```

***

# Use Cases

* Magnetic anomaly detection research

* Autonomous underwater vehicle simulation

* Sensor fusion testing

* Path planning over buried cables

* Drone payload sensor modeling

***

# License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

***

# Author

Created by **KhaledHleis**

GitHub: <https://github.com/KhaledHleis>

***
