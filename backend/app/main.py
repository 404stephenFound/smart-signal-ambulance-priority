import asyncio
import json
import os
import time
import yaml
from datetime import datetime
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Header, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from .models import (
    TelemetryPayload, SignalState, SignalCommand, PriorityRequestModel,
    DetectionPayload, SystemThresholds, UpcomingJunction
)
from .db import init_db, get_db_connection, log_audit, save_ambulance_position, log_signal_event
from .tracking import TrackingTracker
from .signal_fsm import TrafficSignalFSM
from .priority_engine import PriorityDecisionEngine
from .multi_ambulance import MultiAmbulanceCoordinator
from .security import SecurityManager
from .mqtt_client import MQTTBridge

# Config paths
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config", "thresholds.yaml")
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))

app = FastAPI(title="Ambulance Priority & Traffic Signal Management System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core engine instances
tracker = TrackingTracker()
security = SecurityManager()
multi_coordinator = MultiAmbulanceCoordinator()
mqtt_bridge = MQTTBridge()

# Load initial configuration thresholds
thresholds_obj = SystemThresholds()
if os.path.exists(CONFIG_PATH):
    try:
        with open(CONFIG_PATH, "r") as f:
            cfg = yaml.safe_load(f)
            th = cfg.get("thresholds", {})
            sig = cfg.get("signal", {})
            op = cfg.get("operational", {})
            thresholds_obj = SystemThresholds(
                monitor_distance_m=th.get("monitor_distance_m", 1000.0),
                prepare_distance_m=th.get("prepare_distance_m", 500.0),
                request_distance_m=th.get("request_distance_m", 500.0),
                emergency_distance_m=th.get("emergency_distance_m", 150.0),
                request_eta_s=th.get("request_eta_s", 45.0),
                emergency_eta_s=th.get("emergency_eta_s", 12.0),
                yellow_s=sig.get("yellow_s", 3.0),
                all_red_s=sig.get("all_red_s", 2.0),
                min_green_s=sig.get("min_green_s", 5.0),
                normal_green_s=sig.get("normal_green_s", 15.0),
                priority_ttl_s=sig.get("priority_ttl_s", 30.0),
                safety_margin_s=sig.get("safety_margin_s", 3.0),
                max_hold_s=sig.get("max_hold_s", 45.0),
                assisted_timeout_s=op.get("assisted_timeout_s", 10.0),
                mode=op.get("mode", "assisted")
            )
    except Exception as e:
        print(f"[Config] Error loading config: {e}")

engine = PriorityDecisionEngine(thresholds_obj)

# Junctions & FSMs
junction_fsms: Dict[str, TrafficSignalFSM] = {}
cached_junctions: Dict[str, Dict[str, Any]] = {}
cached_approaches: Dict[str, Dict[str, Any]] = {}
cached_segments: List[Dict[str, Any]] = []

# Active tracking states in memory
active_ambulances: Dict[str, Dict[str, Any]] = {}

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)

ws_manager = ConnectionManager()

def load_db_cache():
    global cached_junctions, cached_approaches, cached_segments
    conn = get_db_connection()
    c = conn.cursor()
    
    # Load Junctions
    c.execute("SELECT * FROM junctions")
    junctions = [dict(row) for row in c.fetchall()]
    cached_junctions = {j["junction_id"]: j for j in junctions}
    
    # Load Approaches
    c.execute("SELECT * FROM junction_approaches")
    approaches = [dict(row) for row in c.fetchall()]
    cached_approaches = {a["approach_id"]: a for a in approaches}
    
    # Load Segments
    c.execute("SELECT * FROM road_segments")
    cached_segments = [dict(row) for row in c.fetchall()]
    
    # Initialize FSM for each junction
    for j in junctions:
        jid = j["junction_id"]
        cfg = json.loads(j["config"]) if isinstance(j["config"], str) else j["config"]
        junction_fsms[jid] = TrafficSignalFSM(
            junction_id=jid,
            yellow_s=cfg.get("yellow_s", thresholds_obj.yellow_s),
            all_red_s=cfg.get("all_red_s", thresholds_obj.all_red_s),
            min_green_s=cfg.get("min_green_s", thresholds_obj.min_green_s),
            normal_green_s=cfg.get("normal_green_s", thresholds_obj.normal_green_s),
            priority_ttl_s=thresholds_obj.priority_ttl_s
        )
    conn.close()

# Background FSM tick loop
async def fsm_ticker():
    last_states: Dict[str, str] = {}
    while True:
        try:
            for jid, fsm in list(junction_fsms.items()):
                state = fsm.tick(dt=0.5)
                
                # Check for state transition event
                prev_state = last_states.get(jid)
                if prev_state is not None and prev_state != state.state:
                    try:
                        log_signal_event(
                            junction_id=jid,
                            request_id=state.active_request_id,
                            previous_state=prev_state,
                            new_state=state.state,
                            reason="priority" if state.is_priority else "normal_cycle"
                        )
                    except Exception as e:
                        pass
                last_states[jid] = state.state
                
                # Broadcast signal update only if clients connected
                if ws_manager.active_connections:
                    st_data = state.model_dump() if hasattr(state, "model_dump") else state.dict()
                    if st_data.get("last_heartbeat"):
                        st_data["last_heartbeat"] = str(st_data["last_heartbeat"])
                    await ws_manager.broadcast({
                        "type": "signal_state",
                        "data": st_data
                    })
        except Exception as e:
            print(f"[Ticker Error] {e}")
        await asyncio.sleep(0.5)

@app.on_event("startup")
async def startup_event():
    init_db()
    load_db_cache()
    
    # Setup MQTT callback
    def on_mqtt_msg(topic: str, payload: Dict[str, Any]):
        if "ambulance" in topic and "telemetry" in topic:
            asyncio.create_task(process_telemetry(TelemetryPayload(**payload)))
        elif "detections" in topic:
            asyncio.create_task(process_detection(DetectionPayload(**payload)))
    
    mqtt_bridge.set_on_message(on_mqtt_msg)
    mqtt_bridge.start()
    
    # Start background tick
    asyncio.create_task(fsm_ticker())

async def process_telemetry(telemetry: TelemetryPayload) -> Dict[str, Any]:
    # 1. Security & Plausibility validation
    valid, err_msg = security.validate_telemetry_plausibility(telemetry)
    if not valid:
        log_audit("ambulance", telemetry.ambulance_id, "rejected_telemetry", details={"reason": err_msg})
        return {"status": "rejected", "reason": err_msg}

    # 2. Smooth heading & speed
    heading, smoothed_speed = tracker.smooth_heading_and_speed(
        telemetry.ambulance_id,
        telemetry.lat,
        telemetry.lon,
        telemetry.speed_kmh,
        telemetry.heading_deg
    )

    # 3. Identify upcoming junction
    upcoming = tracker.identify_upcoming_junction(
        telemetry.ambulance_id,
        telemetry.lat,
        telemetry.lon,
        heading,
        smoothed_speed,
        cached_segments,
        cached_approaches,
        cached_junctions
    )

    # 4. Priority Decision Engine evaluation
    req, cmd, action_msg = engine.evaluate(telemetry, upcoming)

    # 5. Route command to FSM if present
    if cmd and upcoming:
        fsm = junction_fsms.get(upcoming.junction_id)
        if fsm:
            fsm.process_command(cmd)
            # Publish to MQTT as well
            mqtt_bridge.publish(f"junction/{upcoming.junction_id}/command", cmd.dict())
            log_audit("system", "priority_engine", "command_sent", target=upcoming.junction_id, details=cmd.dict())

    # 6. Save position and update in-memory active store
    save_ambulance_position(telemetry.dict())
    active_data = {
        "ambulance_id": telemetry.ambulance_id,
        "lat": telemetry.lat,
        "lon": telemetry.lon,
        "speed_kmh": round(smoothed_speed, 1),
        "heading_deg": round(heading, 1),
        "emergency": telemetry.emergency,
        "source": telemetry.source,
        "upcoming": upcoming.dict() if upcoming else None,
        "active_request": req.dict() if req else None,
        "last_seen": datetime.utcnow().isoformat()
    }
    active_ambulances[telemetry.ambulance_id] = active_data

    # 7. Broadcast via WebSocket
    await ws_manager.broadcast({
        "type": "ambulance_update",
        "data": active_data
    })
    if req:
        await ws_manager.broadcast({
            "type": "priority_request",
            "data": req.dict(),
            "action": action_msg
        })

    return {"status": "processed", "active_data": active_data}

async def process_detection(detection: DetectionPayload):
    # Rule F6: CV alone raises alert only, does not activate priority
    await ws_manager.broadcast({
        "type": "alert",
        "title": "Camera Ambulance Detection",
        "message": f"Camera {detection.camera_id} detected ambulance (Confidence: {int(detection.confidence * 100)}%)",
        "level": "INFO",
        "data": detection.dict()
    })

# ============================================================================
# REST Endpoints
# ============================================================================

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "traffic-priority-engine", "time": datetime.utcnow().isoformat()}

@app.post("/auth/login")
def login(payload: Dict[str, str] = Body(...)):
    token = payload.get("token", "token-police")
    user = security.authenticate_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"user": user.dict(), "token": user.token}

@app.get("/junctions")
def list_junctions():
    results = []
    for jid, j in cached_junctions.items():
        fsm = junction_fsms.get(jid)
        st = fsm.tick(0) if fsm else None
        results.append({
            "junction_id": jid,
            "name": j["name"],
            "latitude": j["latitude"],
            "longitude": j["longitude"],
            "state": st.dict() if st else None
        })
    return results

@app.get("/ambulances")
def list_active_ambulances():
    return list(active_ambulances.values())

@app.get("/requests")
def list_priority_requests(status: Optional[str] = None):
    reqs = list(engine.requests.values())
    if status:
        reqs = [r for r in reqs if r.status == status.upper()]
    return [r.dict() for r in reqs]

@app.post("/requests/{req_id}/approve")
async def approve_request(req_id: str, group: str = Query("NS"), authorization: Optional[str] = Header(None)):
    user = security.authenticate_token(authorization)
    officer_id = user.user_id if user else "usr-police-01"

    req, cmd = engine.approve_request(req_id, officer_id, group)
    if not req or not cmd:
        raise HTTPException(status_code=404, detail="Request not found or not in approvable state")

    fsm = junction_fsms.get(req.junction_id)
    if fsm:
        fsm.process_command(cmd)
        mqtt_bridge.publish(f"junction/{req.junction_id}/command", cmd.dict())

    log_audit("police", officer_id, "approve", target=req_id, details={"group": group})
    
    await ws_manager.broadcast({
        "type": "request_status",
        "data": req.dict(),
        "action": "APPROVED"
    })
    return {"status": "APPROVED", "request": req.dict(), "command": cmd.dict()}

@app.post("/requests/{req_id}/reject")
async def reject_request(req_id: str, authorization: Optional[str] = Header(None)):
    user = security.authenticate_token(authorization)
    officer_id = user.user_id if user else "usr-police-01"

    req = engine.reject_request(req_id, officer_id)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    log_audit("police", officer_id, "reject", target=req_id)
    
    await ws_manager.broadcast({
        "type": "request_status",
        "data": req.dict(),
        "action": "REJECTED"
    })
    return {"status": "REJECTED", "request": req.dict()}

@app.post("/junctions/{jid}/resume-normal")
async def resume_normal_signal(jid: str, authorization: Optional[str] = Header(None)):
    fsm = junction_fsms.get(jid)
    if not fsm:
        raise HTTPException(status_code=404, detail="Junction not found")

    now_iso = datetime.utcnow().isoformat()
    cmd = SignalCommand(
        cmd="RESUME_NORMAL",
        seq=int(time.time() * 1000) % 1000000,
        issued_at=now_iso
    )
    fsm.process_command(cmd)
    mqtt_bridge.publish(f"junction/{jid}/command", cmd.dict())
    log_audit("police", "manual_override", "resume_normal", target=jid)
    return {"status": "NORMAL_RESUMED", "junction_id": jid}

@app.get("/config/thresholds")
def get_thresholds():
    return engine.thresholds.dict()

@app.put("/config/thresholds")
def update_thresholds(new_th: SystemThresholds):
    engine.update_thresholds(new_th)
    log_audit("admin", "config_update", "update_thresholds", details=new_th.dict())
    return {"status": "updated", "thresholds": engine.thresholds.dict()}

@app.post("/telemetry")
async def ingest_telemetry(payload: TelemetryPayload):
    """Direct HTTP telemetry endpoint for simulators and web apps."""
    res = await process_telemetry(payload)
    return res

@app.get("/metrics/latency")
def get_latency_metrics():
    """Computes measured end-to-end latencies from DB records for evaluation."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM priority_requests WHERE status IN ('COMPLETED', 'ACTIVE')")
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    
    metrics = {
        "total_requests": len(rows),
        "completed": len([r for r in rows if r["status"] == "COMPLETED"]),
        "samples": rows
    }
    return metrics

# ============================================================================
# WebSocket Endpoint
# ============================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    # Send initial state snapshot
    await websocket.send_json({
        "type": "init_snapshot",
        "junctions": [
            {
                "junction_id": jid,
                "name": j["name"],
                "latitude": j["latitude"],
                "longitude": j["longitude"],
                "state": junction_fsms[jid].tick(0).dict()
            } for jid, j in cached_junctions.items()
        ],
        "ambulances": list(active_ambulances.values()),
        "requests": [r.dict() for r in engine.requests.values()],
        "thresholds": engine.thresholds.dict()
    })
    try:
        while True:
            data = await websocket.receive_json()
            # Handle inbound commands from frontend
            msg_type = data.get("type")
            if msg_type == "approve":
                req_id = data.get("request_id")
                group = data.get("group", "NS")
                engine.approve_request(req_id, "police-ws", group)
            elif msg_type == "reject":
                req_id = data.get("request_id")
                engine.reject_request(req_id, "police-ws")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        ws_manager.disconnect(websocket)

# Serve Frontend static assets
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
def serve_dashboard():
    index_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Frontend not found, please check frontend/ directory"}

@app.get("/ambulance")
def serve_ambulance_app():
    amb_file = os.path.join(FRONTEND_DIR, "ambulance.html")
    if os.path.exists(amb_file):
        return FileResponse(amb_file)
    return {"message": "Ambulance app not found"}
