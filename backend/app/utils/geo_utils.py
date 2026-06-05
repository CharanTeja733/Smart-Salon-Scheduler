from math import atan2, cos, radians, sin, sqrt
from typing import List, Tuple


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two points in kilometers using Haversine formula.
    """
    R = 6371  # Earth's radius in kilometers
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

def filter_by_radius(
    points: List[Tuple[float, float]],  # list of (lat, lng)
    center_lat: float,
    center_lng: float,
    radius_km: float
) -> List[int]:
    """Return indices of points within radius."""
    results = []
    for idx, (lat, lng) in enumerate(points):
        dist = calculate_distance(center_lat, center_lng, lat, lng)
        if dist <= radius_km:
            results.append(idx)
    return results

def create_point(lat: float, lng: float) -> str:
    """Create PostGIS POINT string for database."""
    return f'POINT({lng} {lat})'
