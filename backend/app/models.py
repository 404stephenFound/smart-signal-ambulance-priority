from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime

class TelemetryPayload(BaseModel):
    ambulance_id: str
    lat: float
    lon: float
    speed_kmh: float = 0.0
    heading_deg: Optional[float] = None
    emergency: bool = True
    seq: int = 0
    ts: Optional[str] = None
    source: Literal["simulator", "phone", "camera"] = "simulator"

class UpcomingJunction(BaseModel):
    junction_id: str
    junction_name: str
    approach_id: str
    approach_name: str
    green_group: Literal["NS", "EW"]
    distance_m: float
    eta_s: float
    bearing_diff_deg: float

class SignalState(BaseModel):
    junction_id: str
    state: str  # e.g., "NS_GREEN", "NS_YELLOW", "ALL_RED", "EW_GREEN", "PRIORITY_GREEN_NS", "FAULT_SAFE"
    active_group: Optional[Literal["NS", "EW"]] = None
    is_priority: bool = False
    active_request_id: Optional[str] = None
    remaining_s: float = 0.0
    elapsed_s: float = 0.0
    seq: int = 0
    healthy: bool = True
    last_heartbeat: Optional[datetime] = None

class SignalCommand(BaseModel):
    cmd: Literal["PRIORITY", "HOLD_GREEN", "CANCEL_PRIORITY", "RESUME_NORMAL", "FAULT_SAFE"]
    request_id: Optional[str] = None
    group: Optional[Literal["NS", "EW"]] = None
    ttl_s: float = 30.0
    seq: int = 0
    issued_at: str

class PriorityRequestModel(BaseModel):
    request_id: str
    event_id: Optional[str] = None
    ambulance_id: str
    junction_id: str
    approach_id: str
    distance_m: float
    eta_s: float
    priority_level: Literal["MONITOR", "PREPARE", "REQUEST", "EMERGENCY"]
    status: Literal["REQUESTED", "APPROVED", "REJECTED", "ACTIVE", "COMPLETED", "EXPIRED", "CANCELLED"]
    decided_by: Optional[str] = None
    t_first_detect: Optional[str] = None
    t_alert: Optional[str] = None
    t_decision: Optional[str] = None
    t_command_sent: Optional[str] = None
    t_signal_ack: Optional[str] = None
    t_crossed: Optional[str] = None
    t_normal_restored: Optional[str] = None

class DetectionPayload(BaseModel):
    camera_id: str
    confidence: float
    matched_ambulance_id: Optional[str] = None
    frame_s3_key: Optional[str] = None
    ts: Optional[str] = None

class UserAuth(BaseModel):
    user_id: str
    name: str
    role: Literal["admin", "police", "ambulance_operator"]
    token: str

class SystemThresholds(BaseModel):
    monitor_distance_m: float = 1000.0
    prepare_distance_m: float = 500.0
    request_distance_m: float = 500.0
    emergency_distance_m: float = 150.0
    request_eta_s: float = 45.0
    emergency_eta_s: float = 12.0
    yellow_s: float = 3.0
    all_red_s: float = 2.0
    min_green_s: float = 5.0
    normal_green_s: float = 15.0
    priority_ttl_s: float = 30.0
    safety_margin_s: float = 3.0
    max_hold_s: float = 45.0
    assisted_timeout_s: float = 10.0
    mode: Literal["assisted", "automatic"] = "assisted"
