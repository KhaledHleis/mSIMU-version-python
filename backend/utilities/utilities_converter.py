import numpy as np
def Absolute_position(parent_absolute_position, parent_heading, relative_position):
    """
    Convert a relative position to an absolute position in 3D space given a parent's 
    absolute position and heading.
    
    This function transforms coordinates from a local reference frame (relative to a parent object)
    to a global reference frame. It applies rotation about the z-axis (yaw/heading) and then 
    translates by the parent's absolute position. Roll and pitch are assumed to be zero.
    
    Args:
        parent_absolute_position (tuple or list): The (x, y, z) coordinates of the parent 
            in the absolute/global reference frame.
        parent_heading (float): The heading/yaw angle of the parent in radians. This is the 
            rotation about the z-axis (typically measured counter-clockwise from the positive 
            x-axis when looking down from above).
        relative_position (tuple or list): The (x, y, z) coordinates in the parent's local 
            reference frame that need to be converted to absolute coordinates.
    
    Returns:
        tuple: The (x, y, z) absolute position in the global reference frame.
    """
    import math
    
    # Extract coordinates
    px, py, pz = parent_absolute_position
    rx, ry, rz = relative_position
    
    # Apply rotation transformation based on parent's heading (rotation about z-axis only)
    # 3D rotation matrix for rotation about z-axis (yaw):
    # x' = x*cos(θ) - y*sin(θ)
    # y' = x*sin(θ) + y*cos(θ)
    # z' = z (unchanged)
    rotated_x = rx * math.cos(parent_heading) - ry * math.sin(parent_heading)
    rotated_y = rx * math.sin(parent_heading) + ry * math.cos(parent_heading)
    rotated_z = rz  # z-coordinate unchanged for rotation about z-axis
    
    # Translate by parent's absolute position
    absolute_x = px + rotated_x
    absolute_y = py + rotated_y
    absolute_z = pz + rotated_z
    
    absolute_position = (absolute_x, absolute_y, absolute_z)
    
    return absolute_position