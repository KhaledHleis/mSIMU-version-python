"""
ui/helpers.py  –  shared path helpers and data-loading utilities
"""

from __future__ import annotations
import json, os, glob
from pathlib import Path


# ── Project-root resolution ───────────────────────────────────────────────────
# app.py lives at the project root; __file__ is ui/helpers.py → go one level up.
ROOT = Path(__file__).parent.parent.resolve()


# ── Directory conventions ─────────────────────────────────────────────────────
def drones_dir()       -> Path: return ROOT / "experiments" / "drones"
def worlds_dir()       -> Path: return ROOT / "experiments" / "worlds"
def trajectories_dir() -> Path: return ROOT / "experiments" / "simulated_trajectories"
def real_traj_dir()    -> Path: return ROOT / "experiments" / "real_trajectories"
def manips_dir()       -> Path: return ROOT / "experiments" / "manip"
def logs_dir()         -> Path: return ROOT / "logs"


def _glob_ext(folder: Path, *exts: str) -> list[str]:
    """Return sorted list of file paths with given extensions under *folder*."""
    results = []
    for ext in exts:
        results.extend(sorted(folder.glob(f"**/*.{ext}")))
    return [str(p) for p in results]


# ── File list helpers (return relative names for display) ────────────────────
def list_drones()       -> list[str]: return _glob_ext(drones_dir(),       "json")
def list_worlds()       -> list[str]: return _glob_ext(worlds_dir(),       "json")
def list_trajectories() -> list[str]: return _glob_ext(trajectories_dir(), "csv") \
                                             + _glob_ext(real_traj_dir(),   "csv")
def list_manips()       -> list[str]: return _glob_ext(manips_dir(),        "json")

def list_log_dirs() -> list[str]:
    """Return sorted list of experiment log-folder paths."""
    if not logs_dir().exists():
        return []
    return sorted(
        str(p) for p in logs_dir().iterdir()
        if p.is_dir() and (p / "metadata.json").exists()
    )


# ── JSON loading helpers ──────────────────────────────────────────────────────
def load_json(path: str | Path) -> dict | list | None:
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        return None


def load_drone(path: str) -> dict | None:
    return load_json(path)


def load_world(path: str) -> dict | None:
    return load_json(path)


def load_experiment(path: str) -> dict | None:
    return load_json(path)


# ── Sensor extraction from a drone config ────────────────────────────────────
def get_sensor_names(drone_path: str) -> list[str]:
    d = load_drone(drone_path)
    if not d or "sensors" not in d:
        return []
    return [s["name"] for s in d["sensors"]]


# ── Log metadata ──────────────────────────────────────────────────────────────
def read_log_metadata(log_dir: str) -> dict:
    return load_json(Path(log_dir) / "metadata.json") or {}


def get_log_sensor_names(log_dir: str) -> list[str]:
    """
    Read sensor names from the experiment JSON referenced in metadata,
    or fall back to scanning the CSV files in the log folder.
    """
    meta   = read_log_metadata(log_dir)
    exp_name = meta.get("experiment_name", "")

    # Try to find the matching experiment JSON by experiment_name
    for manip in list_manips():
        d = load_json(manip)
        if d and d.get("experiment_name") == exp_name:
            drone_path = d.get("drone_name", "")
            names = get_sensor_names(drone_path)
            if names:
                return names

    # Fallback: look for manip.csv / manip_gradio.csv columns
    csvs = list(Path(log_dir).glob("manip*.csv"))
    if csvs:
        import pandas as pd
        try:
            df = pd.read_csv(csvs[0], nrows=0)
            return [c.replace("magx_", "").replace("magy_", "").replace("magz_", "")
                    for c in df.columns if c.startswith("magx_")]
        except Exception:
            pass
    return ["sensor_UNO"]   # safe default


# ── Trajectory CSV sample ─────────────────────────────────────────────────────
def read_trajectory_sample(csv_path: str, n: int = 2000):
    """Return a sub-sampled DataFrame suitable for plotting."""
    import pandas as pd
    try:
        df = pd.read_csv(csv_path)
        step = max(1, len(df) // n)
        return df.iloc[::step]
    except Exception:
        return None


# ── Pretty-print a dict as indented JSON ─────────────────────────────────────
def pretty_json(obj) -> str:
    if obj is None:
        return "— (could not load) —"
    return json.dumps(obj, indent=2, ensure_ascii=False)