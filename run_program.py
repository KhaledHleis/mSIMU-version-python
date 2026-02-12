from backend.simulation.parsers.experiment_parser import ExperimentParser
import argparse
import os


def main(config_path):

    exp_parser = ExperimentParser()
    experiment = exp_parser.Parse(config_path)
    experiment.run()
    print(experiment)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="Run simulation with an experiment configuration file"
    )
    ap.add_argument("config", help="Path to experiment configuration file")
    args = ap.parse_args()

    config_path = args.config
    if not os.path.isfile(config_path):
        raise SystemExit(f"Configuration file not found: {config_path}")

    main(config_path)
