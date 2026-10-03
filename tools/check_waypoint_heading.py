"""
Verify that a waypoint file's `heading` column agrees with the course
implied by its own consecutive lon/lat points.

This is the acceptance test for Bug 1. mSIMU converts lon/lat to NED with a
correct pyproj transverse Mercator projection and then obeys the commanded
`heading` verbatim (backend/simulation/experiment.py) — as it should, since
a real platform genuinely can crab. So if the generator laid the waypoints
out in a NAIVE lon/lat space (1 deg of longitude treated as equal in metres
to 1 deg of latitude) while writing headings that match that naive layout,
the simulated drone flies with its nose permanently off its own ground
track, and every dataset produced from that file carries the offset.

Usage:
    python tools/check_waypoint_heading.py experiments/simulated_trajectories/waypoints_60deg_snake.csv

Reports, over the straight legs only, the median difference between the
commanded heading and the course computed two ways. A correctly generated
file shows |metric| < 0.1 deg. A file that shows ~0 deg in the NAIVE column
and several degrees in the METRIC column is the Bug 1 signature.
"""

import argparse

import numpy as np
import pandas as pd
from pyproj import Transformer


def _wrap180(a):
    return (np.asarray(a, float) + 180.0) % 360.0 - 180.0


def courses(lon, lat):
    """Course over ground (deg from North) per sample, metric and naive."""
    lon0, lat0 = float(np.mean(lon)), float(np.mean(lat))
    transformer = Transformer.from_crs(
        "epsg:4326",
        f"+proj=tmerc +lat_0={lat0} +lon_0={lon0} +k=1 +x_0=0 +y_0=0 +ellps=WGS84",
        always_xy=True,
    )
    east, north = transformer.transform(np.asarray(lon), np.asarray(lat))
    metric = np.degrees(np.arctan2(np.gradient(east), np.gradient(north))) % 360.0

    # naive: 1 deg of longitude == 1 deg of latitude, in whatever units
    naive = np.degrees(
        np.arctan2(np.gradient(np.asarray(lon, float)), np.gradient(np.asarray(lat, float)))
    ) % 360.0
    return metric, naive


def check(filename, turn_rate_threshold=0.05, verbose=True):
    df = pd.read_csv(filename)
    for col in ("longitude", "latitude", "heading"):
        if col not in df.columns:
            raise KeyError(f"{filename}: no '{col}' column")

    heading = df["heading"].to_numpy(float)
    metric, naive = courses(df["longitude"].to_numpy(), df["latitude"].to_numpy())

    # straight legs only: turns have a real, legitimate heading rate, and
    # gradient-based course is noisy there
    unwrapped = np.degrees(np.unwrap(np.radians(heading)))
    straight = np.abs(np.gradient(unwrapped)) < turn_rate_threshold
    if straight.sum() < 10:
        straight = np.ones(len(heading), dtype=bool)

    d_metric = _wrap180(metric[straight] - heading[straight])
    d_naive = _wrap180(naive[straight] - heading[straight])
    result = {
        "file": filename,
        "n": int(len(df)),
        "n_straight": int(straight.sum()),
        "median_metric_deg": float(np.median(d_metric)),
        "median_naive_deg": float(np.median(d_naive)),
        "consistent": bool(abs(np.median(d_metric)) < 0.1),
    }

    if verbose:
        print(f"{filename}")
        print(f"  samples {result['n']} ({result['n_straight']} on straight legs)")
        print(f"  course - heading, metric projection : {result['median_metric_deg']:+.4f} deg")
        print(f"  course - heading, naive  lon/lat    : {result['median_naive_deg']:+.4f} deg")
        if result["consistent"]:
            print("  OK — heading matches the course its own positions imply.")
        else:
            print(
                "  BUG 1 — heading does NOT match the metric course. Every dataset\n"
                "  generated from this file has the drone's nose "
                f"{result['median_metric_deg']:+.2f} deg off its\n"
                "  ground track on every leg. Regenerate with tools/generate_waypoints.py.\n"
                "  Until then, analyse those datasets using the yaw from THIS file\n"
                "  (i.e. the INS heading column of the exported CSV), never a course\n"
                "  derived from position."
            )
    return result


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("waypoints", nargs="+", help="waypoint CSV file(s) to check")
    ap.add_argument(
        "--turn-rate-threshold",
        type=float,
        default=0.05,
        help="deg/sample below which a sample counts as being on a straight leg",
    )
    args = ap.parse_args()
    bad = 0
    for f in args.waypoints:
        if not check(f, args.turn_rate_threshold)["consistent"]:
            bad += 1
        print()
    raise SystemExit(1 if bad else 0)
