import pytest
from backend.app.eta import calculate_eta, compute_eta_error_s

def test_eta_calculation():
    # 500m at 50 km/h (13.89 m/s) -> ~36.0s
    eta, stopped = calculate_eta(500.0, 50.0)
    assert 35.0 <= eta <= 37.0
    assert not stopped

def test_eta_stopped_vehicle_floor():
    # Stopped vehicle (speed 0 km/h) -> uses floor speed (5 km/h = 1.389 m/s)
    eta, stopped = calculate_eta(100.0, 0.0, min_speed_kmh=5.0)
    assert stopped is True
    assert 70.0 <= eta <= 73.0

def test_eta_error_computation():
    err = compute_eta_error_s(predicted_eta_s=30.0, t_request_sec=100.0, t_crossing_sec=132.5)
    assert err == 2.5
