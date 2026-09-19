import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from .models import PriorityRequestModel, UpcomingJunction, TelemetryPayload, SystemThresholds, SignalCommand
from .tracking import haversine_distance_m

class PriorityDecisionEngine:
    def __init__(self, thresholds: Optional[SystemThresholds] = None):
        self.thresholds = thresholds or SystemThresholds()
        # active requests: request_id -> PriorityRequestModel
        self.requests: Dict[str, PriorityRequestModel] = {}
        # ambulance_id + junction_id -> request_id
        self.active_amb_junction_map: Dict[str, str] = {}
        # Tracks last crossing state
        self.ambulance_last_distance: Dict[str, float] = {}

    def update_thresholds(self, new_thresholds: SystemThresholds):
        self.thresholds = new_thresholds

    def evaluate(
        self,
        telemetry: TelemetryPayload,
        upcoming: Optional[UpcomingJunction],
        signal_state: Optional[Dict[str, Any]] = None
    ) -> Tuple[Optional[PriorityRequestModel], Optional[SignalCommand], Optional[str]]:
        """
        Evaluates ambulance position and returns:
        (updated_or_new_request, optional_signal_command, action_event_message)
        """
        if not telemetry.emergency or not upcoming:
            # Not in emergency or no upcoming junction
            return None, None, None

        amb_id = telemetry.ambulance_id
        jid = upcoming.junction_id
        dist = upcoming.distance_m
        eta = upcoming.eta_s
        map_key = f"{amb_id}_{jid}"
        now_iso = datetime.utcnow().isoformat()
        now_ts = time.time()

        # Check crossing detection
        # If vehicle was within 50m and is now beyond or distance increased sharply on same approach
        prev_dist = self.ambulance_last_distance.get(amb_id, dist)
        self.ambulance_last_distance[amb_id] = dist

        existing_req_id = self.active_amb_junction_map.get(map_key)
        existing_req = self.requests.get(existing_req_id) if existing_req_id else None

        # Check if ambulance has crossed the junction
        if existing_req and existing_req.status == "ACTIVE":
            if dist <= 15.0 or (prev_dist < 40.0 and dist > prev_dist + 10.0):
                # Ambulance crossed!
                existing_req.status = "COMPLETED"
                existing_req.t_crossed = now_iso
                existing_req.t_normal_restored = now_iso
                del self.active_amb_junction_map[map_key]
                cmd = SignalCommand(
                    cmd="RESUME_NORMAL",
                    request_id=existing_req.request_id,
                    group=upcoming.green_group,
                    seq=int(now_ts * 1000) % 1000000,
                    issued_at=now_iso
                )
                return existing_req, cmd, "AMBULANCE_CROSSED"

        # Determine Priority Level
        t = self.thresholds
        if dist <= t.emergency_distance_m or eta <= t.emergency_eta_s:
            level = "EMERGENCY"
        elif dist <= t.request_distance_m or eta <= t.request_eta_s:
            level = "REQUEST"
        elif dist <= t.prepare_distance_m:
            level = "PREPARE"
        elif dist <= t.monitor_distance_m:
            level = "MONITOR"
        else:
            level = "MONITOR"

        # If no existing request, create one
        if not existing_req:
            req_id = f"req-{uuid.uuid4().hex[:8]}"
            req = PriorityRequestModel(
                request_id=req_id,
                event_id=f"evt-{amb_id}-{int(now_ts)}",
                ambulance_id=amb_id,
                junction_id=jid,
                approach_id=upcoming.approach_id,
                distance_m=dist,
                eta_s=eta,
                priority_level=level,
                status="REQUESTED" if level in ["REQUEST", "EMERGENCY"] else "REQUESTED",
                t_first_detect=now_iso,
                t_alert=now_iso if level in ["PREPARE", "REQUEST", "EMERGENCY"] else None
            )
            self.requests[req_id] = req
            self.active_amb_junction_map[map_key] = req_id

            # In Automatic Mode, activate priority directly if in REQUEST or EMERGENCY
            if self.thresholds.mode == "automatic" and level in ["REQUEST", "EMERGENCY"]:
                req.status = "ACTIVE"
                req.t_decision = now_iso
                req.t_command_sent = now_iso
                cmd = SignalCommand(
                    cmd="PRIORITY",
                    request_id=req.request_id,
                    group=upcoming.green_group,
                    ttl_s=self.thresholds.priority_ttl_s,
                    seq=int(now_ts * 1000) % 1000000,
                    issued_at=now_iso
                )
                return req, cmd, "AUTOMATIC_PRIORITY_ACTIVATED"

            return req, None, "NEW_REQUEST_GENERATED"
        else:
            # Update existing request
            existing_req.distance_m = dist
            existing_req.eta_s = eta
            existing_req.priority_level = level
            if not existing_req.t_alert and level in ["PREPARE", "REQUEST", "EMERGENCY"]:
                existing_req.t_alert = now_iso

            # In Automatic Mode, escalate to ACTIVE if not already
            if self.thresholds.mode == "automatic" and existing_req.status == "REQUESTED" and level in ["REQUEST", "EMERGENCY"]:
                existing_req.status = "ACTIVE"
                existing_req.t_decision = now_iso
                existing_req.t_command_sent = now_iso
                cmd = SignalCommand(
                    cmd="PRIORITY",
                    request_id=existing_req.request_id,
                    group=upcoming.green_group,
                    ttl_s=self.thresholds.priority_ttl_s,
                    seq=int(now_ts * 1000) % 1000000,
                    issued_at=now_iso
                )
                return existing_req, cmd, "AUTOMATIC_PRIORITY_ACTIVATED"

            return existing_req, None, None

    def approve_request(self, request_id: str, officer_id: str, group: str) -> Tuple[Optional[PriorityRequestModel], Optional[SignalCommand]]:
        """Police approval in Assisted Mode."""
        req = self.requests.get(request_id)
        if not req or req.status not in ["REQUESTED", "APPROVED"]:
            return None, None

        now_iso = datetime.utcnow().isoformat()
        now_ts = time.time()
        req.status = "ACTIVE"
        req.decided_by = officer_id
        req.t_decision = now_iso
        req.t_command_sent = now_iso

        cmd = SignalCommand(
            cmd="PRIORITY",
            request_id=req.request_id,
            group=group if group in ["NS", "EW"] else "NS",
            ttl_s=self.thresholds.priority_ttl_s,
            seq=int(now_ts * 1000) % 1000000,
            issued_at=now_iso
        )
        return req, cmd

    def reject_request(self, request_id: str, officer_id: str) -> Optional[PriorityRequestModel]:
        """Police rejection in Assisted Mode."""
        req = self.requests.get(request_id)
        if not req:
            return None
        now_iso = datetime.utcnow().isoformat()
        req.status = "REJECTED"
        req.decided_by = officer_id
        req.t_decision = now_iso
        return req
