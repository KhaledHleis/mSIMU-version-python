"""
Generate a point-by-point waypoint file whose `heading` column is, by
construction, the course its own consecutive lon/lat points imply.

This is the fix for Bug 1. The defect it replaces is a generator that laid
waypoints out in a NAIVE lon/lat space — 1 deg of longitude treated as equal
in metres to 1 deg of latitude — while mSIMU converts the same lon/lat to
NED with a correct pyproj transverse Mercator projection. The commanded
heading then matched the naive layout but not the real ground track, so the
simulated drone flew with its nose ~9.7 deg off its own track on every leg
of every dataset.

The fix is structural, not a correction factor: the whole trajectory is
built in METRES first (straight legs joined by semicircular turns, sampled
at constant ground speed), the heading is read off the path tangent in that
same metric frame, and only then are the points projected back to lon/lat.
There is no step at which the two can disagree.

    python tools/generate_waypoints.py out.csv --course 146.2314 \
        --leg-length 17.8 --spacing 3.0 --n-legs 20 --speed 1.78 --fs 50 \
        --lon0 -4.503754158369759 --lat0 48.49209220724089

Verify any file, generated or legacy, with:

    python tools/check_waypoint_heading.py out.csv

NOTE this deliberately does NOT rewrite the existing waypoints_*.csv files.
Regenerating them changes every dataset derived from them, so it is a
decision for whoever owns those datasets. Until they are regenerated, those
datasets must be analysed using the yaw exported from the waypoint file (the
INS heading column), never a course derived from position — see
backend/simulation/reader.py.
"""

import argparse

import numpy as np
import pandas as pd
from pyproj import Transformer


def _unit(psi_deg):
    """(East, North) unit vector for a heading psi degrees clockwise from North."""
    psi = np.radians(psi_deg)
    return np.array([np.sin(psi), np.cos(psi)])


def snake_path(course_deg, leg_length, spacing, n_legs, ds):
    """
    Boustrophedon ("snake") path in local East/North metres, sampled every
    `ds` metres of arc length. Straight legs on `course_deg` / `course_deg`
    + 180, joined by semicircular turns of radius spacing/2 so the heading
    is continuous and its rate is bounded.

    Returns (east, north, heading_deg), each shape (n,). heading_deg is the
    path tangent, i.e. exactly the course these points imply.
    """
    fwd = _unit(course_deg)                       # along-leg
    right = _unit(course_deg + 90.0)              # leg-to-leg offset
    radius = spacing / 2.0

    east, north, heading = [], [], []

    def emit(points, headings):
        east.extend(points[:, 0])
        north.extend(points[:, 1])
        heading.extend(headings)

    origin = np.zeros(2)
    for i in range(n_legs):
        direction = fwd if i % 2 == 0 else -fwd
        psi = (course_deg if i % 2 == 0 else course_deg + 180.0) % 360.0

        start = origin + i * spacing * right
        n_pts = max(2, int(round(leg_length / ds)))
        s = np.arange(n_pts) * ds
        emit(start + s[:, None] * direction, np.full(n_pts, psi))

        if i == n_legs - 1:
            break

        # semicircular turn onto the next leg: centre sits half a lane
        # across from the leg end, and the platform sweeps 180 deg
        end = start + (n_pts - 1) * ds * direction
        centre = end + radius * right
        n_turn = max(2, int(round(np.pi * radius / ds)))
        # angle of (end - centre) measured in the (right, direction) plane
        sweep = np.linspace(0.0, np.pi, n_turn + 1)[1:-1]
        arc = centre + np.outer(np.cos(sweep), -radius * right) + np.outer(
            np.sin(sweep), radius * direction
        )
        # tangent heading along the arc, turning from psi to psi + 180
        turn_heading = (psi + np.degrees(sweep)) % 360.0
        emit(arc, turn_heading)

    return np.array(east), np.array(north), np.array(heading)


def to_lonlat(east, north, lon0, lat0):
    transformer = Transformer.from_crs(
        f"+proj=tmerc +lat_0={lat0} +lon_0={lon0} +k=1 +x_0=0 +y_0=0 +ellps=WGS84",
        "epsg:4326",
        always_xy=True,
    )
    # same projection mSIMU uses in backend/utilities/utilities_converter.py,
    # so the trajectory the simulator reconstructs is the one built here
    return transformer.transform(east, north)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("output", help="waypoint CSV to write")
    ap.add_argument("--course", type=float, required=True,
                    help="heading of the survey legs, deg clockwise from North")
    ap.add_argument("--leg-length", type=float, default=17.8, help="metres")
    ap.add_argument("--spacing", type=float, default=3.0,
                    help="metres between adjacent legs")
    ap.add_argument("--n-legs", type=int, default=20)
    ap.add_argument("--speed", type=float, default=1.78, help="m/s over ground")
    ap.add_argument("--fs", type=float, default=50.0, help="sample rate, Hz")
    ap.add_argument("--lon0", type=float, default=-4.503754158369759,
                    help="projection origin — use the world file's reference point")
    ap.add_argument("--lat0", type=float, default=48.49209220724089)
    ap.add_argument("--start-east", type=float, default=0.0,
                    help="offset of the first leg's start, metres east of the origin")
    ap.add_argument("--start-north", type=float, default=0.0)
    args = ap.parse_args()

    ds = args.speed / args.fs
    east, north, heading = snake_path(
        args.course, args.leg_length, args.spacing, args.n_legs, ds
    )
    east = east + args.start_east
    north = north + args.start_north

    lon, lat = to_lonlat(east, north, args.lon0, args.lat0)

    n = len(lon)
    dt_us = int(round(1e6 / args.fs))
    df = pd.DataFrame(
        {
            "timestamp": np.arange(n, dtype=np.int64) * dt_us,
            "index": np.arange(1, n + 1),
            "latitude": np.round(lat, 10),
            "longitude": np.round(lon, 10),
            "heading": np.round(heading, 4),
        }
    )
    df.to_csv(args.output, index=False)
    print(f"wrote {args.output}: {n} samples, {args.n_legs} legs, ds={ds:.4f} m")

    # self-check: never ship a waypoint file without proving the property
    # this generator exists to guarantee
    from check_waypoint_heading import check  # noqa: E402  (same directory)

    if not check(args.output)["consistent"]:
        raise SystemExit(
            "generate_waypoints: the file just written FAILS its own heading "
            "consistency check — do not use it."
        )


if __name__ == "__main__":
    import os
    import sys

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
