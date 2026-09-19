import pytest
from backend.app.security import SecurityManager
from backend.app.models import TelemetryPayload

def test_security_unregistered_ambulance():
    sec = SecurityManager()
    tel = TelemetryPayload(ambulance_id="UNKNOWN_999", lat=12.9738, lon=77.6074, emergency=True)
    valid, err = sec.validate_telemetry_plausibility(tel)
    assert valid is False
    assert "Unregistered" in err

def test_security_implausible_speed():
    sec = SecurityManager()
    tel = TelemetryPayload(ambulance_id="A102", lat=12.9738, lon=77.6074, speed_kmh=240.0, emergency=True)
    valid, err = sec.validate_telemetry_plausibility(tel)
    assert valid is False
    assert "Implausible speed" in err

def test_security_valid_telemetry():
    sec = SecurityManager()
    tel = TelemetryPayload(ambulance_id="A102", lat=12.9738, lon=77.6074, speed_kmh=50.0, emergency=True)
    valid, err = sec.validate_telemetry_plausibility(tel)
    assert valid is True
    assert err is None
