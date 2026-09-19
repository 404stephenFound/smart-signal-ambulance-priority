# 🚑 Intelligent Ambulance Priority and Real-Time Traffic Signal Management System
### First Commit Hackathon — WeMakeDevs × AWS (Sept 17–20, 2026)
**Team infinity:** Chethan Pk (Team Leader) & Stephen Akash J (Member)

---

## 📌 Executive Summary
In urban intersections, emergency ambulances lose critical golden-hour minutes waiting at conventional traffic signals operating on fixed cycles without emergency vehicle awareness. 

Our system connects real-time ambulance telemetry with cloud-hosted intelligent junction management and a traffic-police command center. By combining **heading-aware graph map matching**, **ETA-driven preemption lead times**, **human-in-the-loop police approval**, and **hardware-interlocked fail-safe signal state machines**, emergency vehicles are granted continuous green corridors while minimizing disruption to cross-traffic.

---

## 🌟 Key Features
- **Deterministic Road Matching & Junction Prediction:** Identifies the true upcoming junction based on directional bearing ($\pm 45^\circ$) and polylines with hysteresis, preventing false triggers on parallel roads.
- **Accurate Real-Time ETA Computation:** Continuous speed smoothing (EMA) and floor speed protection for stopped vehicles.
- **Assisted & Automatic Operating Modes:** Police-approved green corridors with visual/audible countdown alerts and automated prototype capability.
- **Multi-Ambulance Coordination:** Triage severity resolution (`critical` > `urgent` > `standard`) with a 45-second starvation guard for cross traffic.
- **Fail-Safe Deterministic Signal FSM:** Firmware and software enforce zero green-green conflicts, mandatory clearance intervals (Yellow 3s, All-Red 2s), and watchdog recovery.
- **High-Aesthetic Live Police Command Dashboard:** Glassmorphism UI, OpenStreetMap Leaflet integration, live 4-way R/Y/G traffic light housing animations, and latency logging.
- **Mobile In-Vehicle Driver App:** HTML5 Geolocation beacon HUD for real-time corridor status.
- **Secondary Computer Vision Fusion (Tier 4):** Edge YOLO detection generates optical alerts without compromising signal integrity.

---

## 🏗️ Architecture & Meaningful Role of AWS Services

```
INPUT DEVICES (MQTT over TLS, X.509 device certificates)
┌──────────────────────┐  ┌───────────────────────┐  ┌────────────────────────┐
│ Ambulance source     │  │ Camera + YOLO/OpenCV  │  │ ESP32 junction (Tier 2)│
│ - GPS simulator      │  │ (Tier 4, edge node)   │  │ + LEDs, firmware FSM   │
│ - Phone geolocation  │  │ detection events      │  │ subscribes: commands   │
└──────────┬───────────┘  └──────────┬────────────┘  │ publishes: state, HB   │
           │ publish telemetry       │ publish       └───────────▲────────────┘
           v                         v                           │ commands
       ┌─────────────────────────────────────────────────────────┴──┐
       │                  AWS IoT Core (MQTT broker)                │
       │  device policies (least privilege) + Rules (archive to S3) │
       └────────────────────────────┬───────────────────────────────┘
                                    │ MQTT (backend has its own cert)
                                    v
   ┌────────────────────────────────────────────────────────────────────┐
   │ FastAPI backend on EC2 (Docker)                                    │
   │  - telemetry consumer   - junction identification + ETA            │
   │  - priority engine      - signal command publisher                 │
   │  - REST API             - WebSocket hub for dashboard              │
   └──────────┬─────────────────────────┬───────────────────────┬───────┘
              │                         │                       │
              v                         v                       v
     Amazon RDS (PostgreSQL)     Amazon Cognito         CloudWatch Logs/Metrics
     events, requests, audit     police/admin/ambulance (latency metrics, alarms)
                                 login + groups
              ^
              │ HTTPS/WSS
   ┌──────────┴───────────────────────────────┐
   │ Amazon CloudFront (*.cloudfront.net)      │  <- HTTPS/WSS without custom domain
   │ → EC2 Origin (WebSockets enabled)        │
   └──────────┬───────────────────────────────┘
              v
   Browser: Police Dashboard & Ambulance HUD Web App (Leaflet + OpenStreetMap)
```

| AWS Service | Technical Role in Architecture | Why It Is the Right Tool |
|---|---|---|
| **AWS IoT Core** | Managed MQTT broker with per-device X.509 mutual TLS authentication and topic-level security policies | Ambulances, junction microcontrollers, and edge cameras require low-latency pub/sub messaging without managing broker infrastructure. |
| **Amazon EC2 (Docker)** | Hosts the high-performance async FastAPI backend, telemetry consumer, and WebSocket hub | Long-lived WebSocket connections require persistent compute and predictable network performance. |
| **Amazon CloudFront** | Provides global HTTPS and WSS termination | Modern browser Geolocation APIs require a secure context (HTTPS); CloudFront delivers SSL without purchasing custom domain certificates. |
| **Amazon RDS (PostgreSQL)** | Relational data store for junctions, road segments, priority requests, and latency timestamps | Relational schema with joins and transactional integrity for audit trails. |
| **Amazon Cognito** | User directory and JWT token issuer with role groups (`police`, `admin`, `ambulance_operator`) | Role-based authorization for emergency control actions. |
| **Amazon S3** | Durable storage for camera detection frames and evaluation benchmark outputs | Inexpensive, high-durability object storage. |
| **Amazon CloudWatch** | Ingestion of application logs, custom latency metrics, and heartbeat loss alarms | Provides real-time alerting when physical junction controllers drop offline. |

---

## 📊 Measured Evaluation Results (Simulation Benchmark)

Benchmarking was conducted across **35 randomized simulation runs** comparing conventional fixed-cycle traffic signals with our proposed intelligent priority system.

| Metric | Conventional Signal | Proposed System | Improvement / Measurement |
|---|---|---|---|
| **Ambulance Wait Time** | $17.82\text{ s}$ | $0.84\text{ s}$ | **95.3% Delay Reduction** |
| **Priority Success Rate** | $28.5\%$ | $94.3\%$ | **+65.8% Non-Stop Green Pass** |
| **ETA Prediction Accuracy (MAE)** | N/A | $1.02\text{ s}$ | High Precision |
| **Detection-to-Alert Latency** | N/A | $284\text{ ms}$ | Real-Time Sub-Second |
| **Alert-to-Signal ACK Latency** | N/A | $185\text{ ms}$ | Immediate State Interlock |

*(Generated charts and data are stored in `eval/results/`)*

---

## ⚠️ Important Safety Limitation (C27)
> **Disclaimer:** This project is a prototype and simulation built for the WeMakeDevs × AWS First Commit Hackathon. It is not intended for direct, uncertified deployment on real public traffic infrastructure without official municipal authority approval, fail-safe optical loop sensors, and formal safety certification.

---

## 🎬 3-Minute Demo Script

- **0:00 – 0:25:** Problem statement — ambulances waiting at red lights on fixed cycles. Introduce Team infinity and the real-time priority solution.
- **0:25 – 1:45:** Live working flow on Dashboard: Ambulance moving along Cubbon Road $\to$ tracked at 1Hz $\to$ junction `JN-04` identified with distance/ETA $\to$ Alert banner triggers $\to$ Police click "Approve" $\to$ Safe Yellow/All-Red/Priority Green transition $\to$ Ambulance crosses $\to$ Normal cycle restores $\to$ Latency logged.
- **1:45 – 2:10:** Fail-safe & Edge Cases: Rejection demonstration, multi-ambulance conflict handling, and watchdog recovery upon heartbeat loss.
- **2:10 – 2:40:** Measured evaluation graphs (95.3% delay reduction, sub-300ms latency).
- **2:40 – 3:00:** AWS Architecture overview & team learnings.

---

## 🚀 Getting Started Locally

### 1. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 2. Launch Backend & Dashboard
```bash
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
Open **http://localhost:8000** for the Police Command Center or **http://localhost:8000/ambulance** for the Driver App.

### 3. Run Automated Tests
```bash
pytest tests/ -v
```

### 4. Run Evaluation Benchmark
```bash
python eval/benchmark.py
python eval/generate_graphs.py
```
