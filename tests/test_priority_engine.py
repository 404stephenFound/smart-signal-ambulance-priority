import pytest
from backend.app.priority_engine import PriorityDecisionEngine
from backend.app.models import TelemetryPayload, UpcomingJunction, SystemThresholds

def test_priority_engine_evaluation_assisted():
    th = SystemThresholds(mode="assisted", request_distance_m=500.0, prepare_distance_m=500.0)
    engine = PriorityDecisionEngine(th)

    telemetry = TelemetryPayload(ambulance_id="A102", lat=12.9800, lon=77.6074, emergency=True)
    upcoming = UpcomingJunction(
        junction_id="JN-04",
        junction_name="MG Road",
        approach_id="JN-04-N",
        approach_name="North",
        green_group="NS",
        distance_m=400.0,
        eta_s=30.0,
        bearing_diff_deg=0.0
    )

    req, cmd, action = engine.evaluate(telemetry, upcoming)
    assert req is not None
    assert req.priority_level == "REQUEST"
    assert req.status == "REQUESTED"
    # In assisted mode, cmd is None until police approval
    assert cmd is None

    # Police Approves
    approved_req, approve_cmd = engine.approve_request(req.request_id, "usr-police-01", "NS")
    assert approved_req.status == "ACTIVE"
    assert approve_cmd is not None
    assert approve_cmd.cmd == "PRIORITY"
    assert approve_cmd.group == "NS"

def test_priority_engine_automatic_mode():
    th = SystemThresholds(mode="automatic", request_distance_m=500.0)
    engine = PriorityDecisionEngine(th)

    telemetry = TelemetryPayload(ambulance_id="A102", lat=12.9800, lon=77.6074, emergency=True)
    upcoming = UpcomingJunction(
        junction_id="JN-04",
        junction_name="MG Road",
        approach_id="JN-04-N",
        approach_name="North",
        green_group="NS",
        distance_m=350.0,
        eta_s=25.0,
        bearing_diff_deg=0.0
    )

    req, cmd, action = engine.evaluate(telemetry, upcoming)
    assert req is not None
    assert req.status == "ACTIVE"
    assert cmd is not None
    assert cmd.cmd == "PRIORITY"
