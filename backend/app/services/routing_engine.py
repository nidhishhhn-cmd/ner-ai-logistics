"""
NER Routing Engine
Provides exact turn-by-turn road geometry, curved geodesic flight arcs,
railway freight corridors, and multimodal split routes across Northeast India.
"""
import math
import json
import urllib.request
from typing import List, Dict, Tuple, Optional, Any

# Major railway junction alignment in NER (Northeast Frontier Railway)
RAIL_NETWORK = {
    "Guwahati": [26.1445, 91.7362],
    "Jagiroad": [26.1200, 92.2100],
    "Chaparmukh": [26.1900, 92.5200],
    "Hojai": [26.0000, 92.8600],
    "Lumding": [25.7470, 93.1747],
    "Diphu": [25.8400, 93.4300],
    "Dimapur": [25.9096, 93.7274],
    "Jorhat": [26.7465, 94.2026],
    "Dibrugarh": [27.4728, 94.9120],
    "Tinsukia": [27.4924, 95.3543],
    "Haflong": [25.1700, 93.0200],
    "Badarpur": [24.9000, 92.6000],
    "Silchar": [24.8333, 92.7789],
    "Jiribam": [24.8007, 93.1192],
    "Agartala": [23.8315, 91.2868]
}

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance in kilometers."""
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    return 2.0 * r * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))


def get_exact_road_route(lat1: float, lon1: float, lat2: float, lon2: float) -> Tuple[List[List[float]], float, float]:
    """
    Fetches exact turn-by-turn road geometry from OSRM driving service.
    Returns (waypoints_latlng, distance_km, duration_hours).
    Falls back to realistic interpolated terrain path if offline.
    """
    try:
        url = f"http://router.project-osrm.org/route/v1/driving/{lon1:.5f},{lat1:.5f};{lon2:.5f},{lat2:.5f}?overview=full&geometries=geojson"
        req = urllib.request.Request(url, headers={"User-Agent": "NERLogistics/1.0"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("code") == "Ok" and data.get("routes"):
                route = data["routes"][0]
                coords = route["geometry"]["coordinates"]  # [lon, lat]
                dist_km = round(route["distance"] / 1000.0, 1)
                duration_h = round(route["duration"] / 3600.0, 1)

                # Downsample to ~250 points for fast rendering while preserving high-fidelity turns
                step = max(1, len(coords) // 250)
                decimated = coords[::step]
                if coords[-1] not in decimated:
                    decimated.append(coords[-1])

                latlngs = [[round(pt[1], 5), round(pt[0], 5)] for pt in decimated]
                return latlngs, dist_km, duration_h
    except Exception as err:
        pass

    # Fallback to realistic curved corridor
    direct_dist = haversine_distance(lat1, lon1, lat2, lon2)
    road_dist = round(direct_dist * 1.38, 1)
    duration_h = round(road_dist / 42.0, 1)  # 42 km/h average in hill/highway terrain
    points = interpolate_curved_path(lat1, lon1, lat2, lon2, num_points=40, roughness=0.04)
    return points, road_dist, duration_h


def generate_flight_arc(lat1: float, lon1: float, lat2: float, lon2: float, num_points: int = 40) -> Tuple[List[List[float]], float, float]:
    """
    Generates a realistic curved geodesic flight path (air route) between two airports.
    Returns (waypoints_latlng, flight_distance_km, flight_duration_hours).
    """
    dist_km = haversine_distance(lat1, lon1, lat2, lon2)
    flight_time = round((dist_km / 520.0) + 0.45, 1)  # 520 km/h cruising + 25m taxi/takeoff/approach

    points = []
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    chord_len = math.sqrt(dlat ** 2 + dlon ** 2) or 1.0

    # Perpendicular unit vector to bow the flight path gracefully north/east
    perp_lat = -dlon / chord_len
    perp_lon = dlat / chord_len
    bow = chord_len * 0.16  # 16% arched curvature

    for i in range(num_points + 1):
        t = i / float(num_points)
        base_lat = lat1 + t * dlat
        base_lon = lon1 + t * dlon
        arc_offset = 4.0 * t * (1.0 - t) * bow
        points.append([round(base_lat + perp_lat * arc_offset, 5), round(base_lon + perp_lon * arc_offset, 5)])

    return points, round(dist_km, 1), flight_time


def generate_rail_corridor(lat1: float, lon1: float, lat2: float, lon2: float, origin_name: str, dest_name: str) -> Tuple[List[List[float]], float, float]:
    """
    Generates realistic railway corridor waypoints following the Northeast Frontier Railway (NFR) network.
    """
    # Check if we can build a railway alignment via known junctions
    waypoints = [[lat1, lon1]]

    # Look for matching junction anchors between origin and dest
    mid_points = []
    if "Guwahati" in origin_name and "Imphal" in dest_name:
        mid_points = [
            RAIL_NETWORK["Jagiroad"],
            RAIL_NETWORK["Chaparmukh"],
            RAIL_NETWORK["Hojai"],
            RAIL_NETWORK["Lumding"],
            RAIL_NETWORK["Diphu"],
            RAIL_NETWORK["Dimapur"],
            [25.6701, 94.1101], # Kohima feeder
        ]
    elif "Guwahati" in origin_name and "Silchar" in dest_name:
        mid_points = [
            RAIL_NETWORK["Lumding"],
            RAIL_NETWORK["Haflong"],
            RAIL_NETWORK["Badarpur"],
        ]
    elif "Guwahati" in origin_name and "Dibrugarh" in dest_name:
        mid_points = [
            RAIL_NETWORK["Chaparmukh"],
            RAIL_NETWORK["Lumding"],
            RAIL_NETWORK["Dimapur"],
            RAIL_NETWORK["Jorhat"],
            RAIL_NETWORK["Tinsukia"],
        ]
    else:
        # Interpolate 3-4 gentle curves representing track curvature
        dlat = (lat2 - lat1) / 4.0
        dlon = (lon2 - lon1) / 4.0
        mid_points = [
            [lat1 + dlat * 1 - 0.05, lon1 + dlon * 1 + 0.04],
            [lat1 + dlat * 2 + 0.03, lon1 + dlon * 2 - 0.02],
            [lat1 + dlat * 3 - 0.02, lon1 + dlon * 3 + 0.03],
        ]

    for pt in mid_points:
        waypoints.append([round(pt[0], 5), round(pt[1], 5)])
    waypoints.append([lat2, lon2])

    # Calculate total rail distance along waypoints
    total_dist = 0.0
    for i in range(len(waypoints) - 1):
        total_dist += haversine_distance(waypoints[i][0], waypoints[i][1], waypoints[i+1][0], waypoints[i+1][1])

    rail_dist = round(total_dist * 1.15, 1)
    rail_time = round(rail_dist / 48.0, 1)  # 48 km/h freight train average speed
    return waypoints, rail_dist, rail_time


def interpolate_curved_path(lat1: float, lon1: float, lat2: float, lon2: float, num_points: int = 40, roughness: float = 0.02) -> List[List[float]]:
    """Creates a smooth curved path with slight natural terrain bends."""
    points = []
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    for i in range(num_points + 1):
        t = i / float(num_points)
        # S-curve displacement for realistic mountain road meandering
        wobble = math.sin(t * math.pi * 3) * roughness
        lat = lat1 + t * dlat + wobble
        lon = lon1 + t * dlon + wobble * 0.7
        points.append([round(lat, 5), round(lon, 5)])
    return points
