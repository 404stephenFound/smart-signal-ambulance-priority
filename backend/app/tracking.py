import math
import json
from typing import List, Dict, Any, Optional, Tuple
from .models import UpcomingJunction

def haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates in meters using Haversine formula."""
    R = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

def calculate_bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate forward azimuth bearing from point 1 to point 2 in degrees (0-360)."""
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_lambda = math.radians(lon2 - lon1)

    y = math.sin(delta_lambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - \
        math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda)
    bearing = math.degrees(math.atan2(y, x))
    return (bearing + 360.0) % 360.0

def angle_diff_deg(a1: float, a2: float) -> float:
    """Compute shortest angular difference between two bearings in degrees (0-180)."""
    diff = abs((a1 - a2 + 180.0) % 360.0 - 180.0)
    return diff

class TrackingTracker:
    def __init__(self):
        # ambulance_id -> history of {lat, lon, speed, ts, heading}
        self.ambulance_histories: Dict[str, List[Dict[str, Any]]] = {}
        # ambulance_id -> previous matched segment_id
        self.last_matched_segment: Dict[str, str] = {}
        # ambulance_id -> smoothed speed
        self.smoothed_speeds: Dict[str, float] = {}

    def smooth_heading_and_speed(self, ambulance_id: str, lat: float, lon: float, 
                                speed_kmh: Optional[float], heading_deg: Optional[float]) -> Tuple[float, float]:
        """
        Calculates smoothed heading from consecutive coordinates and smoothed speed using EMA.
        """
        history = self.ambulance_histories.setdefault(ambulance_id, [])
        history.append({"lat": lat, "lon": lon, "speed": speed_kmh or 0.0})
        if len(history) > 10:
            history.pop(0)

        # 1. Compute heading
        computed_heading = heading_deg
        if len(history) >= 2:
            prev = history[-2]
            dist = haversine_distance_m(prev["lat"], prev["lon"], lat, lon)
            if dist > 1.0:  # Only update bearing if moved > 1m to prevent GPS jitter
                computed_heading = calculate_bearing_deg(prev["lat"], prev["lon"], lat, lon)
        
        if computed_heading is None:
            computed_heading = 0.0

        # 2. Smooth speed with EMA (alpha = 0.4)
        current_speed = speed_kmh if speed_kmh is not None else 0.0
        prev_smoothed = self.smoothed_speeds.get(ambulance_id, current_speed)
        smoothed_speed = 0.4 * current_speed + 0.6 * prev_smoothed
        self.smoothed_speeds[ambulance_id] = smoothed_speed

        return computed_heading, smoothed_speed

    def distance_along_polyline(self, lat: float, lon: float, polyline: List[List[float]]) -> float:
        """
        Computes remaining distance from current coordinate along the polyline to its terminus.
        """
        if not polyline:
            return 0.0
        
        # Find closest point / segment index on polyline
        min_dist = float('inf')
        closest_idx = 0
        for i, pt in enumerate(polyline):
            d = haversine_distance_m(lat, lon, pt[0], pt[1])
            if d < min_dist:
                min_dist = d
                closest_idx = i

        # Remaining distance along downstream segments
        rem_dist = haversine_distance_m(lat, lon, polyline[closest_idx][0], polyline[closest_idx][1])
        for i in range(closest_idx, len(polyline) - 1):
            rem_dist += haversine_distance_m(
                polyline[i][0], polyline[i][1],
                polyline[i+1][0], polyline[i+1][1]
            )
        return rem_dist

    def identify_upcoming_junction(
        self,
        ambulance_id: str,
        lat: float,
        lon: float,
        heading_deg: float,
        smoothed_speed_kmh: float,
        road_segments: List[Dict[str, Any]],
        approaches: Dict[str, Dict[str, Any]],
        junctions: Dict[str, Dict[str, Any]],
        max_search_radius_m: float = 1200.0,
        heading_tolerance_deg: float = 55.0
    ) -> Optional[UpcomingJunction]:
        """
        Graph-based map matching algorithm to identify upcoming junction, approach, and along-road distance.
        """
        best_match = None
        min_score = float('inf')
        prev_segment_id = self.last_matched_segment.get(ambulance_id)

        for seg in road_segments:
            polyline = seg["polyline"]
            if isinstance(polyline, str):
                polyline = json.loads(polyline)

            # Distance from current position to segment terminus (junction entry)
            term_lat, term_lon = polyline[-1][0], polyline[-1][1]
            dist_to_term = haversine_distance_m(lat, lon, term_lat, term_lon)

            if dist_to_term > max_search_radius_m:
                continue

            # Approach details
            approach = approaches.get(seg["approach_id"])
            if not approach:
                continue

            app_bearing = approach["bearing_deg"]
            bearing_diff = angle_diff_deg(heading_deg, app_bearing)

            # Check if within heading tolerance
            if bearing_diff > heading_tolerance_deg:
                continue

            # Check if moving away: bearing from vehicle to junction vs heading
            bearing_to_junction = calculate_bearing_deg(lat, lon, term_lat, term_lon)
            diff_to_junction = angle_diff_deg(heading_deg, bearing_to_junction)
            if diff_to_junction > 85.0 and dist_to_term > 35.0:
                # Ambulance is heading away from this junction
                continue

            # Distance along polyline
            along_dist = self.distance_along_polyline(lat, lon, polyline)

            # Score: along_dist + angular penalty - hysteresis bias
            score = along_dist + (bearing_diff * 3.0)
            if seg["segment_id"] == prev_segment_id:
                score -= 60.0  # Hysteresis bonus to prevent flapping

            if score < min_score:
                min_score = score
                jid = seg["to_junction"]
                j_info = junctions.get(jid, {"name": jid})

                # Compute ETA
                v_ms = max(smoothed_speed_kmh, 5.0) / 3.6
                eta_s = along_dist / v_ms

                best_match = UpcomingJunction(
                    junction_id=jid,
                    junction_name=j_info.get("name", jid),
                    approach_id=seg["approach_id"],
                    approach_name=approach.get("name", seg["approach_id"]),
                    green_group=approach["green_group"],
                    distance_m=round(along_dist, 1),
                    eta_s=round(eta_s, 1),
                    bearing_diff_deg=round(bearing_diff, 1)
                )
                self.last_matched_segment[ambulance_id] = seg["segment_id"]

        return best_match
