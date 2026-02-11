import os
import shutil
from datetime import datetime
from backend.simulation.loggers.Convertible_json_Logger import BatchLoggerThread


def create_logger_directory(experiment_name: str, overwrite: bool = False) -> str:
    """
    Create a directory structure for logging experiment data.
    
    Args:
        experiment_name: Name of the experiment (will be used as folder name)
        overwrite: If True, delete existing directory if it exists (default: False)
    
    Returns:
        str: Path to the created experiment directory
    
    Raises:
        FileExistsError: If directory exists and overwrite=False
    """
    # Create base logs directory if it doesn't exist
    base_log_dir = "logs"
    os.makedirs(base_log_dir, exist_ok=True)
    
    # Create experiment directory path
    experiment_dir = os.path.join(base_log_dir, experiment_name)
    
    # Check if directory exists
    if os.path.exists(experiment_dir):
        if overwrite:
            print(f"[Logger] Removing existing directory: {experiment_dir}")
            shutil.rmtree(experiment_dir)
        else:
            raise FileExistsError(
                f"Experiment directory '{experiment_dir}' already exists. "
                f"Use overwrite=True to replace it or choose a different experiment name."
            )
    
    # Create directory structure
    os.makedirs(experiment_dir, exist_ok=True)
    os.makedirs(os.path.join(experiment_dir, "drone"), exist_ok=True)
    os.makedirs(os.path.join(experiment_dir, "world"), exist_ok=True)
    
    # Optionally create a metadata file
    metadata_path = os.path.join(experiment_dir, "metadata.json")
    metadata = {
        "experiment_name": experiment_name,
        "created_at": datetime.now().isoformat(),
        "description": ""
    }
    
    import json
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"[Logger] Created experiment directory: {experiment_dir}")
    return experiment_dir


def initialize_loggers_batch(experiment_name: str, batch_size: int = 10, flush_frequency: float = 1, overwrite: bool = False):
    """
    Initialize batch loggers for drone and world data.
    
    Args:
        experiment_name: Name of the experiment
        batch_size: Number of items to accumulate before writing (default: 10)
        flush_frequency: How many times per second to flush (default: 1 Hz)
        overwrite: If True, overwrite existing experiment directory (default: False)
    
    Returns:
        tuple: (drone_logger, world_logger) - BatchLoggerThread instances
    
    Example:
        >>> drone_logger, world_logger = initialize_loggers_batch("exp_001", batch_size=20, flush_frequency=2)
        >>> drone_logger.log(drone_state)
        >>> world_logger.log(world_state)
    """
    # Create directory structure
    create_logger_directory(experiment_name, overwrite=overwrite)
    
    # Calculate flush interval (inverse of frequency)
    flush_interval = 1.0 / flush_frequency if flush_frequency > 0 else 1.0
    
    # Initialize drone logger
    drone_logger = BatchLoggerThread(
        log_dir=os.path.join("logs", experiment_name, "drone"),
        batch_size=batch_size,
        flush_interval=flush_interval,
    )
    
    # Initialize world logger
    world_logger = BatchLoggerThread(
        log_dir=os.path.join("logs", experiment_name, "world"),
        batch_size=batch_size,
        flush_interval=flush_interval,
    )
    
    print(f"[Logger] Initialized loggers for experiment '{experiment_name}'")
    print(f"[Logger] Batch size: {batch_size}, Flush frequency: {flush_frequency} Hz")
    
    return drone_logger, world_logger


def initialize_loggers_batch_with_timestamp(base_name: str, batch_size: int = 10, flush_frequency: float = 1):
    """
    Initialize batch loggers with an auto-generated timestamp in the experiment name.
    Useful to avoid directory conflicts.
    
    Args:
        base_name: Base name for the experiment
        batch_size: Number of items to accumulate before writing (default: 10)
        flush_frequency: How many times per second to flush (default: 1 Hz)
    
    Returns:
        tuple: (drone_logger, world_logger, experiment_name)
    
    Example:
        >>> drone_logger, world_logger, exp_name = initialize_loggers_batch_with_timestamp("training_run")
        >>> # exp_name might be: "training_run_20260211_143052"
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    experiment_name = f"{base_name}_{timestamp}"
    
    drone_logger, world_logger = initialize_loggers_batch(
        experiment_name=experiment_name,
        batch_size=batch_size,
        flush_frequency=flush_frequency,
        overwrite=False  # No need to overwrite since timestamp makes it unique
    )
    
    return drone_logger, world_logger, experiment_name