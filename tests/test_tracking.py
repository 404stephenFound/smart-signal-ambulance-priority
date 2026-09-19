import pytest
import math
from backend.app.tracking import (
    haversine_distance_m,
    calculate_bearing_deg,
    angle_diff_deg,
    TrackingTracker
)
from backend.app.models import UpcomingJunction

def test_haversine_distance():
    # MG Road to Brigade Road junction in Bangalore (~200m)
    d = haversine_distance_m(12.9738, 77.6074, 12.9755, 77.6074)
    assert 180.0 < d < 200.0

def test_bearing_calculation():
    # Pure North -> South is 180 degrees
    bearing = calculate_bearing_deg(12.9800, 77.6074, 12.9700, 77.6074)
    assert pytest.approx(bearing, 0.1) == 180.0

    # Pure West -> East is 90 degrees
    bearing_ew = calculate_bearing_deg(12.9738, 77.6000, 12.9738, 77.6100)
    assert pytest.approx(bearing_ew, 0.1) == 90.0

def test_angle_difference():
    assert angle_diff_deg(10.0, 350.0) == 20.0
    assert angle_diff_deg(180.0, 180.0) == 0.0
    assert angle_diff_deg(0.0, 180.0) == 180.0

def test_tracking_map_matching():
    tracker = TrackingTracker()
    segments = [{
        "segment_id": "SEG-N-01",
        "to_junction": "JN-04",
        "polyline": [[12.9820, 77.6074], [12.9738, 77.6074]],
        "approach_id": "JN-04-N"
    }]
    approaches = {
        "JN-04-N": {"name": "North", "bearing_deg": 180.0, "green_group": "NS"}
    }
    junctions = {
        "JN-04": {"name": "MG Road Junction"}
    }

    # Ambulance moving South towards JN-04 at 12.9800, 77.6074 with heading 180
    match = tracker.identify_upcoming_junction(
        ambulance_id="A102",
        lat=12.9800,
        lon=77.6074,
        heading_deg=180.0,
        smoothed_speed_kmh=45.0,
        road_segments=segments,
        approaches=approaches,
        junctions=junctions
    )

    assert match is not None
    assert match.junction_id == "JN-04"
    assert match.approach_id == "JN-04-N"
    assert match.green_group == "NS"
    assert match.distance_m > 0
    assert match.eta_s > 0
