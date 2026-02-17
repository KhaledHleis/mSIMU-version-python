import numpy as np
from pyproj import Transformer

def export_csv_from_reader():
    pass

def COO_to_LLD(input: np.ndarray, ref: np.ndarray) -> np.ndarray:
    """
    Convert local Cartesian coordinates (NED frame, meters) back to GNSS coordinates (longitude, latitude, depth).
    
    Parameters:
    - input: np.ndarray, shape (N, 3), columns = [x_north, y_east, z_down]
    - ref: np.ndarray, shape (1, 3), reference point [longitude, latitude, depth]
    
    Returns:
    - np.ndarray of shape (N, 3), GNSS coordinates [longitude, latitude, depth]
    """

    # Validate input
    assert input.ndim == 2 and input.shape[1] == 3, f"Input must be 2D with 3 columns, got {input.shape}"
    assert ref.ndim == 2 and ref.shape == (1, 3), f"Reference must have shape (1,3), got {ref.shape}"

    # Extract reference longitude, latitude, and depth
    lon0, lat0, depth0 = ref[0]

    # Setup the same local TM projection used in the forward transform
    transformer = Transformer.from_crs(
        "epsg:4326",
        f"+proj=tmerc +lat_0={lat0} +lon_0={lon0} +k=1 +x_0=0 +y_0=0 +ellps=WGS84",
        always_xy=True
    )

    # NED -> ENU: x_east = y_ned, y_north = x_ned
    x_ned = input[:, 0]  # North
    y_ned = input[:, 1]  # East
    z_ned = input[:, 2]  # Down

    x_enu = y_ned  # East
    y_enu = x_ned  # North

    # Inverse transform from local TM projection back to lon/lat
    lons = []
    lats = []
    for x, y in zip(x_enu, y_enu):
        lon, lat = transformer.transform(x, y, direction="INVERSE")
        lons.append(lon)
        lats.append(lat)
    lons = np.array(lons)
    lats = np.array(lats)

    # Recover depth: z_down = depth - depth0  =>  depth = z_down + depth0
    depths = z_ned + depth0

    return np.stack([lons, lats, depths], axis=1)