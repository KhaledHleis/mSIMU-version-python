import numpy as np
from pyproj import Transformer

def export_csv_from_reader():
    pass

def ned_to_lld(input: np.ndarray, ref: np.ndarray) -> np.ndarray:
    """
    Convert local Cartesian NED coordinates in meters to GNSS coordinates (longitude, latitude, depth).
    
    Parameters:
    - input: np.ndarray, shape (N, 3), local coordinates in meters in NED frame [x_north, y_east, z_down]
    - ref: np.ndarray, shape (1, 3), reference point [longitude, latitude, depth]
    
    Returns:
    - np.ndarray of shape (N, 3), columns = [longitude, latitude, depth]
    """

    # Validate input
    assert input.ndim == 2 and input.shape[1] == 3, f"Input must be 2D with 3 columns, got {input.shape}"
    assert ref.ndim == 2 and ref.shape == (1, 3), f"Reference must have shape (1,3), got {ref.shape}"

    # Extract reference longitude, latitude, and depth
    lon0, lat0, depth0 = ref[0]

    # Setup a local ENU (East-North-Up) projection using pyproj
    transformer = Transformer.from_crs(
        f"+proj=tmerc +lat_0={lat0} +lon_0={lon0} +k=1 +x_0=0 +y_0=0 +ellps=WGS84",  # Local tangent plane
        "epsg:4326",  # WGS84 Lat/Lon
        always_xy=True
    )

    # Convert NED to ENU: ENU = [E, N, U] = [y_ned, x_ned, -z_ned]
    y_enu = input[:, 0]  # North → East
    x_enu = input[:, 1]  # East → North
    z_enu = -input[:, 2] # Down → Up

    # Transform all points back to lon/lat
    lons = []
    lats = []
    for x_east, y_north in zip(x_enu, y_enu):
        lon, lat = transformer.transform(x_east, y_north)
        lons.append(lon)
        lats.append(lat)
    lons = np.array(lons)
    lats = np.array(lats)

    # Depth as z (positive down in both frames)
    depths = z_enu + depth0

    return np.column_stack([lons, lats, depths])