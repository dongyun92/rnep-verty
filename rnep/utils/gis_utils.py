"""
GIS utility functions for coordinate transformations and calculations
"""
import math
from typing import List, Tuple, Optional
from shapely.geometry import LineString, Point
from pyproj import Transformer, CRS
import geopandas as gpd
from geopy.distance import geodesic

from rnep.scenario.models import Position, Waypoint


def transform_coordinates(
    geometry,
    from_crs: str = "EPSG:4326",
    to_crs: str = "EPSG:4326"
) -> any:
    """
    Transform coordinates between different coordinate reference systems.
    
    Args:
        geometry: Shapely geometry object
        from_crs: Source CRS (default: WGS84)
        to_crs: Target CRS (default: WGS84)
        
    Returns:
        Transformed geometry
    """
    if from_crs == to_crs:
        return geometry
    
    transformer = Transformer.from_crs(
        CRS(from_crs),
        CRS(to_crs),
        always_xy=True
    )
    
    if hasattr(geometry, 'coords'):
        # Handle LineString, LinearRing
        transformed_coords = [
            transformer.transform(x, y) for x, y in geometry.coords
        ]
        return type(geometry)(transformed_coords)
    elif hasattr(geometry, 'x'):
        # Handle Point
        x, y = transformer.transform(geometry.x, geometry.y)
        return Point(x, y)
    else:
        raise ValueError(f"Unsupported geometry type: {type(geometry)}")


def calculate_distance(
    pos1: Position,
    pos2: Position,
    unit: str = "km"
) -> float:
    """
    Calculate distance between two positions using geodesic distance.
    
    Args:
        pos1: First position
        pos2: Second position
        unit: Unit of distance ("km", "m", "miles")
        
    Returns:
        Distance in specified unit
    """
    point1 = (pos1.lat, pos1.lon)
    point2 = (pos2.lat, pos2.lon)
    
    distance = geodesic(point1, point2)
    
    if unit == "km":
        return distance.kilometers
    elif unit == "m":
        return distance.meters
    elif unit == "miles":
        return distance.miles
    else:
        raise ValueError(f"Unsupported unit: {unit}")


def extract_waypoints_from_linestring(
    linestring: LineString,
    altitude: Optional[float] = None
) -> List[Waypoint]:
    """
    Extract waypoints from a LineString geometry.
    
    Args:
        linestring: Shapely LineString object
        altitude: Default altitude if not provided in geometry
        
    Returns:
        List of Waypoint objects
    """
    waypoints = []
    coords = list(linestring.coords)
    
    for i, coord in enumerate(coords):
        # Handle both 2D and 3D coordinates
        if len(coord) == 3:
            lon, lat, alt = coord
        else:
            lon, lat = coord
            alt = altitude or 0.0
        
        position = Position(lat=lat, lon=lon, alt=alt)
        
        # Calculate distance from previous waypoint
        distance_from_previous = 0.0
        if i > 0:
            prev_position = waypoints[i-1].position
            distance_from_previous = calculate_distance(prev_position, position)
        
        waypoint = Waypoint(
            id=f"WP{i+1:03d}",
            sequence=i,
            position=position,
            distance_from_previous=distance_from_previous
        )
        waypoints.append(waypoint)
    
    return waypoints


def calculate_total_distance(waypoints: List[Waypoint]) -> float:
    """
    Calculate total distance of a flight path.
    
    Args:
        waypoints: List of waypoints
        
    Returns:
        Total distance in kilometers
    """
    return sum(wp.distance_from_previous for wp in waypoints)


def calculate_bearing(
    pos1: Position,
    pos2: Position
) -> float:
    """
    Calculate bearing between two positions.
    
    Args:
        pos1: Start position
        pos2: End position
        
    Returns:
        Bearing in degrees (0-360)
    """
    lat1 = math.radians(pos1.lat)
    lat2 = math.radians(pos2.lat)
    lon1 = math.radians(pos1.lon)
    lon2 = math.radians(pos2.lon)
    
    dlon = lon2 - lon1
    
    y = math.sin(dlon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - \
        math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    
    bearing = math.atan2(y, x)
    bearing = math.degrees(bearing)
    bearing = (bearing + 360) % 360
    
    return bearing


def validate_shapefile(file_path: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a shapefile for flight path import.
    
    Args:
        file_path: Path to shapefile
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Read shapefile
        gdf = gpd.read_file(file_path)
        
        # Check if empty
        if len(gdf) == 0:
            return False, "Shapefile is empty"
        
        # Check geometry type
        geom_types = gdf.geometry.type.unique()
        if not all(gt in ["LineString", "MultiLineString"] for gt in geom_types):
            return False, f"Invalid geometry type. Expected LineString, got {geom_types}"
        
        # Check CRS
        if gdf.crs is None:
            return False, "No coordinate reference system defined"
        
        return True, None
        
    except Exception as e:
        return False, f"Error reading shapefile: {str(e)}"


def create_buffer_zone(
    geometry,
    distance: float,
    crs: str = "EPSG:4326"
) -> any:
    """
    Create a buffer zone around a geometry.
    
    Args:
        geometry: Shapely geometry object
        distance: Buffer distance in meters
        crs: Coordinate reference system
        
    Returns:
        Buffered geometry
    """
    # Convert to a projected CRS for accurate buffering
    if crs == "EPSG:4326":
        # Use UTM zone based on centroid
        centroid = geometry.centroid
        utm_zone = int((centroid.x + 180) / 6) + 1
        utm_crs = f"EPSG:326{utm_zone:02d}" if centroid.y >= 0 else f"EPSG:327{utm_zone:02d}"
        
        # Transform to UTM
        geometry_utm = transform_coordinates(geometry, crs, utm_crs)
        
        # Create buffer
        buffer_utm = geometry_utm.buffer(distance)
        
        # Transform back
        buffer = transform_coordinates(buffer_utm, utm_crs, crs)
    else:
        buffer = geometry.buffer(distance)
    
    return buffer