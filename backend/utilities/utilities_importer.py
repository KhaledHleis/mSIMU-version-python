import numpy as np
from pyproj import Transformer

def LLD_to_Coo(input: np.ndarray, ref: np.ndarray) -> np.ndarray:
    """
    Convert GNSS coordinates (longitude, latitude, depth) to local Cartesian coordinates in meters.
    
    Parameters:
    - input: np.ndarray, shape (N, 3), columns = [longitude, latitude, depth]
    - ref: np.ndarray, shape (1, 3), reference point [longitude, latitude, depth]
    
    Returns:
    - np.ndarray of shape (N, 3), local coordinates in meters [x_east, y_north, z_down]
    """

    # Validate input
    assert input.ndim == 2 and input.shape[1] == 3, f"Input must be 2D with 3 columns, got {input.shape}"
    assert ref.ndim == 2 and ref.shape == (1, 3), f"Reference must have shape (1,3), got {ref.shape}"

    # Extract reference longitude, latitude, and depth
    lon0, lat0, depth0 = ref[0]

    # Setup a local ENU (East-North-Up) projection using pyproj
    transformer = Transformer.from_crs(
        "epsg:4326",  # WGS84 Lat/Lon
        f"+proj=tmerc +lat_0={lat0} +lon_0={lon0} +k=1 +x_0=0 +y_0=0 +ellps=WGS84",  # Local tangent plane
        always_xy=True
    )

    # Transform all points
    x_local = []
    y_local = []
    for lon, lat, depth in input:
        x, y = transformer.transform(lon, lat)
        x_local.append(x)
        y_local.append(y)
    x_local = np.array(x_local)
    y_local = np.array(y_local)

    # Depth as z in local coordinates (positive down)
    z_local = input[:, 2] - depth0

    # Stack as (N, 3)
    local_coords = np.stack([x_local, y_local, z_local], axis=1)

    return local_coords