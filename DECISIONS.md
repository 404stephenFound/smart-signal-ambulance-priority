# Technical Decisions Log — Team infinity

This document records the non-obvious engineering decisions, rationale, and defensible architectural choices for the **Intelligent Ambulance Priority & Real-Time Traffic Signal Management System** (WeMakeDevs × AWS Hackathon, Sept 2026).

---

### D01: Framework Selection — FastAPI over Flask or Node.js
- **Decision:** Use Python FastAPI for the central backend service.
- **Rationale:** FastAPI offers native asynchronous concurrency (`asyncio`), built-in WebSocket support for real-time dashboard updates, automatic OpenAPI/Swagger documentation, and high-performance Pydantic data validation without mixing multiple runtime environments.

### D02: Real-Time Protocol Layering — AWS IoT Core (MQTT) + WebSocket
- **Decision:** Split device telemetry (MQTT via AWS IoT Core) and dashboard UI streaming (WebSocket via FastAPI).
- **Rationale:** Microcontrollers (ESP32), camera nodes, and ambulance GPS trackers require lightweight, pub/sub messaging over TLS with per-device X.509 certificate authentication (MQTT). Web browsers interacting with the control room require bidirectional JSON frames without browser-side MQTT broker certificate overhead (WebSocket).

### D03: Heading-Aware Map Matching vs Simple Nearest Signal
- **Decision:** Implement graph-based road segment matching with directional bearing tolerance ($\pm 45^\circ$) and hysteresis, rather than simple Euclidean / Haversine distance to the nearest signal.
- **Rationale:** A simple radius check triggers false priority requests for signals on parallel roads, overpasses, or junctions the ambulance has already crossed. Heading-aware segment matching ensures preemption is requested only for the junction ahead in the ambulance's actual direction of travel.

### D04: Deterministic Firmware-Enforced Signal Interlock
- **Decision:** Enforce signal safety rules (never green-green for conflicting groups, mandatory minimum yellow ($3\text{s}$) and all-red ($2\text{s}$) clearance times, and minimum green ($5\text{s}$)) inside the Signal State Machine (both in Python reference and ESP32 firmware).
- **Rationale:** The cloud/backend must never be trusted with physical safety. Even if the backend crashes, transmits corrupt commands, or experiences network lag, the junction controller strictly prevents unsafe signal states and safely falls back to standard cycle / fault-safe mode.

### D05: Assisted-First Operating Mode with Timed Escalation
- **Decision:** Default to Assisted Mode (human traffic police in-the-loop) with early `PREPARE` alerts, rather than fully autonomous signal preemption.
- **Rationale:** Public safety and operational trust require human oversight. The system alerts the police early (500m–1km out) so approval can be granted well before the ambulance arrives. If approval times out, visual/audible alerts escalate. Automatic mode is retained strictly as a configurable simulation prototype.

### D06: Multi-Ambulance Priority Heuristic
- **Decision:** Group approaching ambulances by conflict group (`NS` vs `EW`). Merge compatible requests into an extended green corridor. Resolve conflicting requests using triage severity (`critical` > `urgent` > `standard`), then ETA, then least traffic disruption, bounded by a 45s cross-traffic starvation guard.
- **Rationale:** First-come-first-served fails in emergency scenarios where an ambulance with a critical patient or closer ETA would be blocked by an earlier-detected non-critical transport.

### D07: Secondary-Only Computer Vision Fusion (Tier 4)
- **Decision:** Computer vision (YOLO) ambulance detection is strictly a secondary verification signal.
- **Rationale:** Camera detections alone (without verified GPS telemetry and operator authentication) raise a visual control-room alert but NEVER trigger traffic light changes, protecting the intersection from optical spoofing and false positives.
