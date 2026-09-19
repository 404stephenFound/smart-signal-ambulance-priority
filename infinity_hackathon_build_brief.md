# Team infinity — First Commit Hackathon Build Brief
## Intelligent Ambulance Priority and Real-Time Traffic Signal Management System

**Written:** Saturday, September 19, 2026
**Team:** infinity (Chethan Pk — Team Leader, Stephen Akash J — Member)
**Hackathon:** First Commit, WeMakeDevs × AWS, Sept 17–20, 2026

This file is the single source of truth for the building agent and the two humans. It contains, in order:

- **Part A** — hackathon rules and judging context (nothing dropped from the original context document)
- **Part B** — honest fit assessment of this idea and the scope strategy
- **Part C** — the full project specification (all 29 sections of the original idea)
- **Part D** — AWS architecture and the complete technology stack, with the role of every technology
- **Part E** — data model
- **Part F** — core algorithms (junction identification, ETA, priority engine, multi-ambulance, signal state machine)
- **Part G** — messaging, topics and API contracts
- **Part H** — security
- **Part I** — testing and evaluation
- **Part J** — build plan, repository layout, instructions for the building agent
- **Part K** — demo script and submission checklist
- **Part L** — risks and fallbacks

---

# PART A — Hackathon context and rules

## A1. Event overview

- **Hackathon:** First Commit. **Organizer:** WeMakeDevs / AWS.
- **Dates:** September 17–20, 2026.
- **Format:** Online across India, with an optional in-person hack day in Bangalore on September 19, 2026. The Bangalore event does **not** add to the judging score; judging is by the online submission.
- **Team size:** 1–4. Current team: **infinity**, 2/4 members.

## A2. Core objective

The theme is open. The project must **build something that solves a real problem**, from any sector. The principle is:

**Real problem → useful solution → working product.**

Do not start by choosing an AWS technology and inventing a problem around it. Start with the problem and user, then choose the technology.

## A3. AWS requirement

Two tracks:

- **Build It:** build locally with AWS open-source tooling (Strands Agents SDK, Cedar, SAM Local, PartyRock, OpenSearch, Finch, EKS Distro, EKS Anywhere, LocalStack). No AWS account, card, or bill needed.
- **Ship It:** deploy using AWS services (SageMaker AI, EKS, ECS, Fargate, Lambda, API Gateway, Step Functions, EC2, Lightsail, App Runner, Amplify Hosting, S3, DynamoDB, RDS, Aurora, Cognito, CloudFront, Route 53, EventBridge, SQS, SNS, CloudWatch). A new AWS account starts with up to $200 in free credits per the hackathon information.

**Critical rule:** using an AWS open-source project or AWS services is **mandatory to win a prize**. AWS must not be attached at the end. It must have a technically meaningful role in the architecture (Part D explains each role).

## A4. Judging criteria

1. **Idea and Impact** — real problem? what changes for users? clearly defined? "A small problem solved well beats a big problem solved vaguely."
2. **Built on AWS** — meaningful use of the AWS open-source stack or AWS services.
3. **Learning** — what the team actually learned in the hackathon (new service, first deployment, new architecture pattern). Do not fabricate.
4. **Execution** — the project must work. "One feature that runs beats five that almost do."
5. **Demo video** — a **three-minute recorded video** showing what it does, who it is for, the real problem, the working product, and where AWS fits. There is no live demo; the video is what judges see.

## A5. Project selection philosophy and idea evaluation

Order: identify the problem → define the user → define the core solution → define the smallest useful MVP → decide where AWS belongs → check four-day (now ~36-hour) feasibility.

Every idea is evaluated on: real problem, specific user, pain level, MVP feasibility, AWS relevance, demo clarity, technical depth, defensibility, impact, scope. Explain strengths, weaknesses, risks and trade-offs rather than assigning arbitrary scores. Part B applies this to the current idea.

## A6. Failure modes to avoid

1. Technology-first thinking.
2. AI for the sake of AI (chatbots, agents, RAG, computer vision, LLMs added without solving a real part of the problem).
3. Too many features; ten incomplete features lose to one complete workflow.
4. Fake AWS integration (one service bolted on for the submission).
5. Huge problem statement ("we are solving healthcare").
6. A demo that describes instead of demonstrating.
7. Building something the team cannot defend. Amazon fast-track interviews may follow, so every decision must be explainable.

## A7. Career opportunity

The top 10 students from top projects can skip screening rounds and get fast-track Amazon interviews (internships and full-time roles). The project should double as a technically defensible portfolio piece. Be ready to explain: problem, users, architecture, AWS services, data flow, core algorithm, security, limitations, learnings, and why the architecture makes sense.

## A8. Available resources

AWS Builder Center student verification, AWS hands-on workshops, free AWS workshop sandboxes, builder profile, AWS open-source tools, AWS Free Tier, possible extra credits, and the optional Bangalore day (workshops, project feedback, Amazon team interaction, networking, swag).

## A9. Default strategy phases

Problem discovery → brutal filtering → select one problem → simplest architecture → meaningful AWS integration → MVP core workflow → reliability testing of the actual user journey → UI/UX polish → three-minute demo centred on **Problem → User → Solution → Working workflow → AWS → Impact**.

## A10. How agents should help (applies to the building agent)

Use this document as base context. Do not force AI/agents into the solution. Do not recommend AWS services without stating their role. Prioritise a working MVP over feature quantity. Challenge weak assumptions. Flag technical risks early. Keep the timeline and the three-minute demo in mind. Only make recommendations a two-person team can execute.

## A11. Time reality

The hackathon ends **Sept 20**; today is **Sept 19**. There is roughly **a day and a half**, not four days. **Confirm the exact submission cutoff** on the WeMakeDevs hackathon page and count backwards. Feature freeze at least 4 hours before the cutoff; the last 4 hours are for README, diagram, demo video and submission only. Do not submit in the last 15 minutes.

---

# PART B — Honest fit assessment and scope strategy

## B1. What is strong about this idea

- **Real, easy-to-explain problem:** an ambulance waiting at a signal loses time, and signals follow fixed cycles without knowing an emergency vehicle is approaching.
- **Clear users:** traffic-police/control-room operators (dashboard) and ambulance drivers/operators (app).
- **Demo is visual:** a moving ambulance on a map, an alert, an approval click, and a signal changing (virtual, and physically on the ESP32 model).
- **AWS fits naturally:** ambulance and junction devices need a secure real-time message broker, which is what AWS IoT Core is (Part D).
- **Technical depth:** geometry/heading-based junction identification, ETA, a priority engine, a conflict-free signal state machine, fail-safe behaviour, security, measurable results.

## B2. What is risky (challenge the assumptions)

1. **Scope is far beyond a day and a half.** The full specification includes hardware, computer vision, multi-ambulance logic, cloud deployment, security and an evaluation study. Doing all of it at once will produce "five features that almost work", which the judging criteria specifically punish.
2. **Hardware dependency.** An ESP32 that connects to AWS IoT Core over TLS needs certificates, Wi-Fi at the demo location and wiring. Any of these can fail. The demo must not depend on it.
3. **Existing solutions.** Emergency-vehicle signal preemption exists in various forms. Be ready to say what is different here: **heading-based junction identification, ETA-driven timing, human-in-the-loop approval, fail-safe firmware, and measured results.**
4. **Impact claims.** Do not claim lives saved or quote delay statistics you cannot source. Present measured **simulation results** honestly as simulation results.
5. **Safety and legal framing.** This is a prototype. It must never be presented as software that controls real public traffic signals (Section C27).
6. **All the listed technologies together** (FastAPI, SQL database, MQTT and WebSocket, ESP32, OpenCV/YOLO, OpenStreetMap, GPS simulation and geolocation API) is a lot to integrate. It is achievable only in **tiers with cut lines**.

## B3. Scope strategy: tiers with cut lines

Every technology in the specification is included in this plan. They are built in this order, and **a tier is only started when the previous tier works end to end on the deployed stack.** Unfinished tiers are left out of the demo and listed honestly as "future work".

| Tier | Contents | Rule |
|---|---|---|
| **Tier 1 — Must ship** | GPS simulator → AWS IoT Core (MQTT) → FastAPI backend → junction identification, distance, ETA → priority engine → police dashboard (WebSocket, OpenStreetMap map, Approve/Reject) → **virtual** junction signal (same state machine as firmware) → PostgreSQL (RDS) event log → Cognito login → deployed on AWS | This alone is a complete, demoable project |
| **Tier 2 — Hardware** | ESP32 miniature four-way junction with LEDs, connected via MQTT, safe transitions, fail-safe watchdog | Only if the hardware is in hand and Tier 1 is deployed and stable |
| **Tier 3 — Measurement and robustness** | Baseline vs proposed comparison study with tables and graphs, latency measurements, multiple-ambulance handling, phone geolocation ambulance app, false-request protection | Evaluation graphs are high value; do them before YOLO |
| **Tier 4 — Computer vision** | OpenCV + YOLO ambulance detection (and optionally traffic density), events published over MQTT, frames stored in S3 | Advanced; CV never becomes a dependency of the core flow |
| **Future work** | AI-based ETA prediction, route prediction, historical analytics, police mobile notifications, multi-junction priority, Bedrock-generated incident reports | Listed in README only unless time is left |

---

# PART C — Full project specification

## C1. Project concept

A real-time intelligent traffic management system that reduces the time an emergency ambulance spends waiting at traffic intersections.

The system detects or receives information about an approaching ambulance, tracks its location and direction, identifies the upcoming junction, calculates distance and estimated arrival time, decides whether priority is required, notifies traffic police, and provides controlled priority at the right intersection. It combines software, real-time communication, location tracking, intelligent decision-making, and a physical/simulated traffic-signal prototype.

It must **not** be a simple "Ambulance detected → traffic light becomes green" system. It must determine:

> Which ambulance is approaching, where is it going, which junction will it reach, when will it reach it, does it require priority, and what should the traffic signal do?

## C2. Problem statement

Ambulances lose critical time waiting at traffic signals, especially in peak traffic. Conventional signals follow predefined cycles without knowing an emergency vehicle is approaching. The proposed system connects ambulance location information with junction control and a traffic-police monitoring interface so an approaching ambulance gets real-time priority at the required intersection, while minimising unnecessary disruption to other traffic.

**One-sentence version for the submission (narrow and concrete):**

> At a signalised junction, an approaching ambulance has no way to tell the signal it is coming and the control room has no live view of it; this system tracks the ambulance, predicts when it reaches the junction, and gives police-approved, fail-safe green priority at exactly the right moment, then restores the normal cycle.

**Users:** (1) traffic-police / control-room operators; (2) ambulance drivers/operators.
**Current workflow:** the ambulance waits for the signal cycle or relies on sirens and manual clearing by police at the junction.
**Consequence:** lost minutes on time-critical trips.

## C3. Main objective

The system should:

1. Detect or identify an ambulance in an emergency.
2. Receive its real-time or simulated GPS location.
3. Determine its direction of travel.
4. Identify the upcoming traffic junction.
5. Calculate distance from the junction.
6. Estimate arrival time.
7. Determine whether priority should be activated.
8. Send a real-time alert to traffic police/control-room personnel.
9. Allow priority approval in assisted mode.
10. Control a simulated traffic signal in the prototype.
11. Give green priority to the ambulance's route.
12. Prevent conflicting directions from receiving green simultaneously.
13. Detect when the ambulance has crossed the junction.
14. Return the signal to its normal cycle.
15. Record the complete emergency event.

## C4. Overall system workflow

```text
Ambulance
   ↓
Detection / GPS Information
   ↓
Location + Speed + Direction
   ↓
Upcoming Junction Identification
   ↓
Distance Calculation
   ↓
ETA Calculation
   ↓
Priority Decision Engine
   ↓
Traffic Police Notification
   ↓
Priority Approval / Automatic Emergency Decision
   ↓
Traffic Signal Controller
   ↓
Signal Priority
   ↓
Ambulance Crosses Junction
   ↓
Normal Signal Cycle Restored
   ↓
Event Recorded
```

## C5. Ambulance detection

**Primary method: GPS/mobile-based identification.** A simulated or real ambulance application transmits: Ambulance ID, latitude, longitude, speed, direction, emergency status, timestamp.

```text
Ambulance ID: A102
Location: Latitude / Longitude
Speed: 42 km/h
Direction: North → South
Emergency: TRUE
Timestamp: Current time
```

This is the primary implementation because it makes real-time tracking easy to demonstrate. Two GPS sources are supported: (a) a **simulator script** that replays a route along real map coordinates at a configurable speed (repeatable for demos and evaluation), and (b) a **browser geolocation app** on a phone using the Geolocation API (real-device proof; needs HTTPS, see Part D).

**Optional advanced method: Computer Vision.** A camera with YOLO/OpenCV detects an ambulance.

```text
Traffic Camera → Object Detection → Ambulance Detected → Detection Event → Tracking / Priority System
```

Computer vision is an **advanced feature**; the project never depends on it. A CV-only detection (no matching GPS track) raises a **police alert only** and never activates priority by itself (Part F, F6).

## C6. Real-time ambulance tracking

Continuously determine: current location, speed, direction, upcoming junction, distance to junction, estimated arrival time, emergency status.

```text
Ambulance A102
Current location → Distance to Junction J04 = 420 m → Estimated arrival = 32 seconds → Priority request generated
```

GPS data may be simulated if real ambulance data is unavailable.

## C7. Junction identification

Determine which junction the ambulance is approaching, using its **direction and route**, not simply the nearest signal.

```text
Ambulance → Road A → Junction J04 → Traffic Signal
```

The algorithm is in Part F, F1.

## C8. ETA calculation

Simple implementation: **ETA = Distance / Speed**, updated continuously as the ambulance moves, with correct unit conversion.

```text
Distance = 500 m, Speed = 50 km/h
50 km/h ÷ 3.6 = 13.89 m/s → ETA = 500 ÷ 13.89 ≈ 36 seconds
```

More advanced ETA prediction can use traffic conditions and historical data (future work). Details and edge cases are in Part F, F2.

## C9. Priority decision engine

A dedicated component, not a single distance threshold. It considers: emergency status, distance, ETA, direction, junction, current signal state, existing priority request, other emergency vehicles, traffic conditions.

```text
IF emergency = TRUE
AND ambulance is approaching a junction
AND ETA is below configured threshold
AND priority has not already been granted
THEN generate priority request
```

Thresholds are configurable:

```text
Distance > 1 km        → Monitoring
500 m – 1 km           → Prepare
< 500 m                → Priority Request
Very close to junction → Emergency Priority
```

The full engine is in Part F, F3.

## C10. Traffic police dashboard

A web-based dashboard for traffic police/control-room personnel, updating in real time without page refreshes.

```text
TRAFFIC CONTROL DASHBOARD

🚑 AMBULANCE DETECTED
Ambulance ID: A102
Distance: 380 m
ETA: 27 seconds
Direction: North → South
Next Junction: JN-04

Current Signal: East-West GREEN
Priority: REQUESTED
```

Controls: **Approve Priority**, **Reject Priority**, **Monitor**.

## C11. Two operating modes

**Assisted Mode (recommended operational mode):** ambulance detected → system calculates priority → traffic police receive alert → police review → police approve → signal priority activated → ambulance crosses → normal cycle restored. Provides human oversight.

**Automatic Emergency Mode (controlled prototype only):** ambulance detected → algorithm verifies emergency → system activates priority → required route becomes GREEN → conflicting routes remain RED → ambulance crosses → normal cycle restored. Must be clearly presented as a prototype/simulation, not a system for directly controlling real public traffic infrastructure.

**Design point to state in the demo:** police approval takes time. In assisted mode the system alerts early (Prepare zone) so approval can arrive before the ambulance is too close. If no decision arrives within `ASSISTED_TIMEOUT_S`, the alert escalates (repeat, sound, highlight). Automatic activation happens only if the operating mode allows it (Part F, F3).

## C12. Traffic signal prototype

A miniature traffic intersection using an ESP32 or similar microcontroller: four-way road, red/yellow/green LEDs, optional pedestrian signals, model ambulance.

```text
Normal:                     North-South → GREEN, East-West → RED
Ambulance from North:       North-South → PRIORITY GREEN, East-West → RED
After the ambulance passes: return to normal cycle
```

Signals use **safe transitions** (yellow, all-red clearance) and never change conflicting signals abruptly. The state machine is in Part F, F5.

## C13. Real-time communication

The system must demonstrate real real-time communication. The technologies considered were MQTT, WebSockets, REST, HTTP and Firebase real-time services. **Final decision:**

- **MQTT** (via AWS IoT Core) for the device layer: ambulance telemetry, CV detection events, signal commands and state.
- **WebSocket** (FastAPI) from backend to the police dashboard for live updates.
- **REST/HTTP** (FastAPI) for login, approvals, configuration and history.
- Firebase real-time services are not used: they would duplicate MQTT/WebSocket and sit outside AWS.

```text
Ambulance location changes → backend receives update → ETA recalculated → dashboard updated
→ priority status updated → signal controller receives command
```

## C14. Backend

The central system: ambulance information, GPS updates, junction information, ETA calculation, priority decisions, traffic-police requests, signal commands, real-time communication, event logging. **One framework: Python FastAPI** (async, native WebSockets, automatic API docs). Flask and Node.js are not combined with it.

## C15. Database

Stored entities: Ambulance, Junction, Priority Request, Signal Event, User. The normalised design (with additional tables) is in Part E. **PostgreSQL on Amazon RDS.**

## C16. Map interface

The dashboard includes a map showing: ambulance location, ambulance route, upcoming junction, traffic signal, direction of travel, distance, ETA. **Leaflet with OpenStreetMap tiles.** If tiles are unavailable, a simulated road-map canvas is the fallback.

## C17. Multiple ambulance scenario (advanced)

Two ambulances approaching the same junction must not be handled first-detected-first. Evaluate ETA, distance, emergency status, direction, current signal state, existing priority, and junction availability. The documented priority mechanism is in Part F, F4.

## C18. Optional traffic density detection (advanced)

```text
Camera → Vehicle Detection → Traffic Density → Priority Algorithm
```

Density can influence how the signal transitions (e.g., longer clearance for a queued approach) while still giving the ambulance priority. Only after the core system works. Part D, D6.

## C19. Security and authentication

Prototype-level: ambulance authentication, traffic-police login, role-based access, secure API requests, ambulance ID validation, protection against false emergency requests, logging of signal-control actions. Detailed in Part H.

## C20. Testing scenarios

1. **No ambulance:** normal signal operation.
2. **Ambulance far away:** monitored, no priority.
3. **Ambulance approaching:** priority request generated.
4. **Police approves:** signal priority activated.
5. **Ambulance crosses:** normal operation resumes.
6. **Police rejects:** signal stays normal.
7. **Multiple ambulances:** priority follows the defined algorithm.
8. **Communication failure:** system fails safe and avoids unsafe signal behaviour.

Additional scenarios are in Part I.

## C21. Evaluation metrics

Detection accuracy, GPS update frequency, ETA accuracy, detection-to-alert latency, alert-to-signal latency, ambulance waiting time, normal traffic waiting time, signal transition time, priority success rate, dashboard response time. Compare the **conventional signal** (ambulance follows the normal cycle) against the **proposed system** (controlled priority) using tables and graphs. Method in Part I.

## C22. Technology stack (all included)

| Layer | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript (React only if required) |
| Backend | Python FastAPI |
| Database | PostgreSQL |
| Real-time communication | MQTT and WebSocket (plus REST) |
| Hardware | ESP32, LED traffic signals |
| AI / Computer vision | Python, OpenCV, YOLO |
| Location | GPS simulation and browser geolocation API |
| Map | OpenStreetMap |

"Do not use every technology unnecessarily" was part of the original text. The resolution: **every layer above is used, and each has a stated job (Part D). Where the original listed alternatives for the same job (Flask/FastAPI/Node.js, MySQL/PostgreSQL/Firebase, React/plain JS), one is chosen and the others are documented as considered.**

## C23. Minimum working version

Ambulance GPS simulation, real-time backend, junction identification, distance calculation, ETA calculation, priority algorithm, traffic-police dashboard, ESP32 traffic-light prototype, real-time signal control, database/event logging. This must be completed before advanced features. **For the hackathon, the ESP32 item is Tier 2 and a virtual junction with the identical state machine stands in until the hardware works (Part B3).**

## C24. Advanced features

1. YOLO ambulance detection
2. Computer-vision traffic density detection
3. Multiple ambulance handling
4. AI-based ETA prediction
5. Route prediction
6. Mobile ambulance application
7. Police mobile notifications
8. Multi-junction priority
9. Historical traffic analytics
10. Cloud deployment
11. Emergency vehicle authentication
12. Automatic incident reports

Advanced features must improve the system, not just increase the feature count. In this plan: 1, 2, 3, 6, 10 and 11 are in Tiers 3–4 and Tier 1; 4, 5, 7, 8, 9 and 12 are future work (Part B3).

## C25. Final demonstration

```text
AMBULANCE STARTS MOVING → LOCATION RECEIVED → AMBULANCE TRACKED
→ UPCOMING JUNCTION IDENTIFIED → DISTANCE CALCULATED → ETA CALCULATED
→ PRIORITY REQUEST GENERATED → TRAFFIC POLICE ALERT → PRIORITY APPROVED
→ TRAFFIC SIGNAL CHANGES → AMBULANCE CROSSES → SIGNAL RETURNS TO NORMAL
→ EVENT STORED IN DATABASE
```

Shown on a miniature intersection (when Tier 2 works), the dashboard, and real-time status. The 3-minute video script is in Part K.

## C26. Project architecture (layers)

```text
┌─────────────────────────────────────────┐
│             INPUT LAYER                 │
│ GPS / Mobile App / Camera / Sensors     │
└───────────────────┬─────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│          DETECTION & TRACKING           │
│ Location / Direction / Speed / Detection│
└───────────────────┬─────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│        PROCESSING & PREDICTION          │
│ Distance / ETA / Junction Identification│
└───────────────────┬─────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│          PRIORITY DECISION ENGINE       │
│ Emergency + ETA + Signal + Traffic      │
└───────────────┬───────────────┬─────────┘
                ↓               ↓
       ┌────────────────┐  ┌────────────────┐
       │ Police         │  │ Signal Control │
       │ Dashboard      │  │ / ESP32        │
       └────────────────┘  └───────┬────────┘
                                   ↓
                           Traffic Signal
                                   ↓
                              Ambulance
                                   ↓
                         Normal Operation
```

A database/logging component is connected to the backend. The AWS deployment of these layers is in Part D.

## C27. Important safety limitation

This is a college prototype and simulation. It must not be presented as software that can directly control real public traffic signals without authorisation and safety certification. A real deployment would require: traffic-authority approval, secure communication, fail-safe signal control, reliable positioning, cybersecurity, hardware validation, integration with existing infrastructure, and legal/operational approval. The physical implementation therefore uses a miniature junction. **Say this in the README and in the demo video.**

## C28. Development approach (original phases)

1. Ambulance location simulation
2. Backend and database
3. Junction detection, distance and ETA
4. Priority algorithm
5. Traffic-police dashboard
6. ESP32 traffic-signal prototype
7. Connect backend to the physical signal
8. Real-time communication
9. Advanced AI / computer vision
10. Testing and measurable results

Do not start advanced AI before the basic end-to-end system works. The hackathon-adapted build order is in Part J.

## C29. Expected final outcome

An ambulance approaches → the system knows where it is → determines where it is going → identifies the next junction → calculates ETA → determines priority → alerts traffic police → provides controlled signal priority → the ambulance crosses → normal traffic is restored → the event is recorded. The final project must be technically understandable, demonstrable, measurable, and realistic enough to explain in a presentation or viva. Improvements should prioritise usefulness, technical meaning, measurability and feasibility over complexity.

---

# PART D — AWS architecture and complete technology stack

## D1. Architecture diagram

```text
 INPUT DEVICES (MQTT over TLS, X.509 device certificates)
 ┌──────────────────────┐  ┌───────────────────────┐  ┌────────────────────────┐
 │ Ambulance source     │  │ Camera + YOLO/OpenCV  │  │ ESP32 junction (Tier 2)│
 │ - GPS simulator      │  │ (Tier 4, edge laptop) │  │ + LEDs, firmware FSM   │
 │ - Phone geolocation  │  │ detection events      │  │ subscribes: commands   │
 └──────────┬───────────┘  └──────────┬────────────┘  │ publishes: state, HB   │
            │ publish telemetry       │ publish       └───────────▲────────────┘
            v                         v                           │ commands
        ┌────────────────────────────────────────────────────────┴──┐
        │                  AWS IoT Core (MQTT broker)               │
        │  device policies (least privilege) + Rules (archive to S3)│
        └───────────────────────────┬───────────────────────────────┘
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
   │ Amazon CloudFront (default *.cloudfront  │  <- gives HTTPS/WSS without a domain
   │ .net cert) → EC2 origin (WebSocket OK)   │
   └──────────┬───────────────────────────────┘
              v
   Browser: Police dashboard (HTML/CSS/JS + Leaflet/OpenStreetMap)
            Ambulance web app (Geolocation API) — served from the same origin
   S3: detection frames, evaluation artifacts, exported incident logs
   SNS (optional): email/SMS alert to police in addition to the dashboard
```

## D2. Why AWS is here (meaningful roles, not decoration)

| Service | Role in this project | Why it is the right tool |
|---|---|---|
| **AWS IoT Core** | Managed MQTT broker for ambulances, junction controllers and cameras; per-device X.509 identity and topic-level policies | The problem is literally devices exchanging real-time messages; IoT Core provides secure MQTT and device identity without running a broker |
| **EC2** | Runs the FastAPI backend (REST + WebSocket + MQTT client) in Docker | WebSockets need a long-lived server; simplest reliable hosting for a two-person team |
| **CloudFront** | Puts HTTPS/WSS in front of the EC2 origin | Browser geolocation requires a secure context; CloudFront's default domain gives a valid certificate without buying a domain |
| **RDS (PostgreSQL)** | Relational store for ambulances, junctions, requests, signal events, audit log | Data is relational, needs joins and integrity constraints; RDS handles backups and patching |
| **Cognito** | Police/admin/ambulance-operator login and role groups; JWTs verified by the backend | Role-based access for a system with emergency-control actions; avoids writing password storage |
| **S3** | Detection frames, evaluation outputs, IoT-rule archive of raw telemetry | Cheap durable object storage |
| **CloudWatch** | Backend logs, custom latency metrics, an alarm on "junction heartbeat lost" | Ties directly to the fail-safe and latency-measurement requirements |
| **SNS (optional)** | Police email/SMS alert alongside the dashboard | Second alert channel; the "police mobile notification" feature |

**Not used, on purpose:** Bedrock, SageMaker, agents or RAG. Nothing in the core problem needs them. An LLM-written incident report is possible later, but a templated report from the event log comes first. Firebase is not used (it would duplicate the database and MQTT/WebSocket layers and is not AWS).

## D3. Stack decisions in detail

| Need | Chosen | Alternatives from the original list and why not |
|---|---|---|
| Frontend | HTML + CSS + vanilla JavaScript, Leaflet for the map | React "if required" — not required for three screens; reduces build tooling risk |
| Backend | Python FastAPI (uvicorn), `paho-mqtt` or AWS IoT Device SDK for the broker connection | Flask / Node.js — one framework only, as the spec says |
| Database | PostgreSQL on RDS | MySQL — equivalent; Firebase — duplicates real-time layer and is outside AWS |
| Device messaging | MQTT via AWS IoT Core | — |
| Browser live updates | WebSocket (FastAPI) | Polling — defeats the real-time requirement |
| Control/config/history | REST (FastAPI) | — |
| Location input | GPS simulator (repeatable) **and** browser Geolocation API (real device) | — |
| Map | Leaflet + OpenStreetMap tiles | Amazon Location Service is an optional alternative only if OSM tiles are blocked |
| Hardware | ESP32 (Arduino framework or ESP-IDF), 220–330 Ω resistors, LEDs | — |
| Computer vision | Python + OpenCV + YOLO (Ultralytics), fine-tuned on a public ambulance dataset | — |
| Auth | Cognito user pool + groups (`police`, `admin`, `ambulance_operator`) | — |
| Tests | pytest; a simulation harness for evaluation; matplotlib for graphs | — |

## D4. Networking notes (avoid these traps)

- **HTTPS is required for the phone geolocation app.** Browsers only expose the Geolocation API in secure contexts (HTTPS or localhost). Serve the dashboard and ambulance app through CloudFront so both get HTTPS and `wss://`.
- **Mixed content:** a page on HTTPS cannot open a plain `ws://` socket. Use the same CloudFront origin for the SPA, REST and WebSocket.
- CloudFront supports WebSocket connections; set the EC2 (or ALB) as a custom origin and forward the required headers. If this proves troublesome, an ALB with an ACM certificate on a domain is the alternative.
- **ESP32 to IoT Core** uses TLS on port 8883 with the device certificate; it needs Wi-Fi and correct system time. Use a phone hotspot for the demo and test on that network beforehand.

## D5. ESP32 hardware notes (Tier 2)

- Minimum: six LEDs (one R/Y/G set for the North-South group, one for the East-West group). Full: twelve LEDs (R/Y/G per approach).
- Avoid input-only GPIOs (34–39) and boot-strapping pins for LEDs. Use current-limiting resistors on every LED.
- Optional: an IR break-beam or reflective sensor at the junction to confirm crossing physically; optional pedestrian LEDs.
- **The safety interlock lives in the firmware**, not the backend (Part F, F5).
- Fallback chain if IoT Core TLS on the ESP32 takes too long: (1) ESP32 → local Mosquitto broker on a laptop, bridged to the backend; (2) ESP32 polling a REST endpoint. Document whichever is used honestly.

## D6. Computer vision notes (Tier 4)

- **Detection:** YOLO (small model) fine-tuned on a public ambulance dataset; run with OpenCV on a laptop against a webcam pointed at the model junction or a recorded video. Publish `detections/{cameraId}` events over MQTT; store the triggering frame in S3.
- **Safety:** CV is a **secondary signal**. GPS + CV agreement raises confidence; CV alone triggers a police alert but never a signal change (F6).
- **Metrics:** precision, recall and mAP on a held-out set; report as measured.
- **Traffic density (optional):** count vehicle classes (car, bus, truck, motorcycle) per approach region of interest to influence clearance time; only after everything else works.

---

# PART E — Data model (PostgreSQL)

```sql
CREATE TABLE users (
  user_id       UUID PRIMARY KEY,
  cognito_sub   TEXT UNIQUE NOT NULL,
  name          TEXT NOT NULL,
  role          TEXT NOT NULL CHECK (role IN ('admin','police','ambulance_operator')),
  created_at    TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE ambulances (
  ambulance_id     TEXT PRIMARY KEY,            -- e.g. 'A102'
  vehicle_number   TEXT UNIQUE NOT NULL,
  operator_user_id UUID REFERENCES users(user_id),
  iot_thing_name   TEXT UNIQUE,
  active           BOOLEAN DEFAULT TRUE
);

CREATE TABLE junctions (
  junction_id    TEXT PRIMARY KEY,              -- e.g. 'JN-04'
  name           TEXT NOT NULL,
  latitude       DOUBLE PRECISION NOT NULL,
  longitude      DOUBLE PRECISION NOT NULL,
  iot_thing_name TEXT UNIQUE,
  config         JSONB NOT NULL                 -- yellow_s, all_red_s, min_green_s, phases
);

CREATE TABLE road_segments (
  segment_id    TEXT PRIMARY KEY,
  from_junction TEXT REFERENCES junctions(junction_id),  -- NULL for entry roads
  to_junction   TEXT NOT NULL REFERENCES junctions(junction_id),
  polyline      JSONB NOT NULL,                 -- ordered [lat, lon] points
  length_m      DOUBLE PRECISION NOT NULL,
  approach_id   TEXT NOT NULL                   -- which approach of to_junction this feeds
);

CREATE TABLE junction_approaches (
  approach_id   TEXT PRIMARY KEY,               -- e.g. 'JN-04-N'
  junction_id   TEXT NOT NULL REFERENCES junctions(junction_id),
  name          TEXT NOT NULL,                  -- 'North'
  bearing_deg   DOUBLE PRECISION NOT NULL,      -- direction of travel INTO the junction
  green_group   TEXT NOT NULL                   -- 'NS' or 'EW' (conflict group)
);

CREATE TABLE ambulance_positions (
  id           BIGSERIAL PRIMARY KEY,
  ambulance_id TEXT NOT NULL REFERENCES ambulances(ambulance_id),
  ts           TIMESTAMPTZ NOT NULL,
  latitude     DOUBLE PRECISION NOT NULL,
  longitude    DOUBLE PRECISION NOT NULL,
  speed_kmh    DOUBLE PRECISION,
  heading_deg  DOUBLE PRECISION,
  emergency    BOOLEAN NOT NULL,
  source       TEXT CHECK (source IN ('simulator','phone','camera'))
);

CREATE TABLE emergency_events (                 -- one per ambulance trip
  event_id     UUID PRIMARY KEY,
  ambulance_id TEXT NOT NULL REFERENCES ambulances(ambulance_id),
  started_at   TIMESTAMPTZ NOT NULL,
  ended_at     TIMESTAMPTZ,
  mode         TEXT CHECK (mode IN ('assisted','automatic'))
);

CREATE TABLE priority_requests (
  request_id      UUID PRIMARY KEY,
  event_id        UUID REFERENCES emergency_events(event_id),
  ambulance_id    TEXT NOT NULL REFERENCES ambulances(ambulance_id),
  junction_id     TEXT NOT NULL REFERENCES junctions(junction_id),
  approach_id     TEXT NOT NULL REFERENCES junction_approaches(approach_id),
  distance_m      DOUBLE PRECISION,
  eta_s           DOUBLE PRECISION,
  priority_level  TEXT CHECK (priority_level IN ('MONITOR','PREPARE','REQUEST','EMERGENCY')),
  status          TEXT CHECK (status IN ('REQUESTED','APPROVED','REJECTED','ACTIVE',
                                         'COMPLETED','EXPIRED','CANCELLED')),
  decided_by      UUID REFERENCES users(user_id),
  -- latency instrumentation (all timestamptz):
  t_first_detect  TIMESTAMPTZ, t_alert TIMESTAMPTZ, t_decision TIMESTAMPTZ,
  t_command_sent  TIMESTAMPTZ, t_signal_ack TIMESTAMPTZ,
  t_crossed       TIMESTAMPTZ, t_normal_restored TIMESTAMPTZ
);

CREATE TABLE signal_events (
  event_id       BIGSERIAL PRIMARY KEY,
  junction_id    TEXT NOT NULL REFERENCES junctions(junction_id),
  request_id     UUID REFERENCES priority_requests(request_id),
  previous_state TEXT NOT NULL,
  new_state      TEXT NOT NULL,
  reason         TEXT NOT NULL,                 -- 'normal_cycle','priority','recovery','fault_safe'
  ts             TIMESTAMPTZ NOT NULL
);

CREATE TABLE detection_events (                 -- Tier 4
  id            BIGSERIAL PRIMARY KEY,
  camera_id     TEXT NOT NULL,
  confidence    DOUBLE PRECISION NOT NULL,
  matched_ambulance_id TEXT REFERENCES ambulances(ambulance_id),
  frame_s3_key  TEXT,
  ts            TIMESTAMPTZ NOT NULL
);

CREATE TABLE audit_log (
  id            BIGSERIAL PRIMARY KEY,
  ts            TIMESTAMPTZ NOT NULL DEFAULT now(),
  actor_type    TEXT NOT NULL,                  -- 'user','ambulance','system','junction'
  actor_id      TEXT NOT NULL,
  action        TEXT NOT NULL,                  -- 'approve','reject','activate','override','login_fail','rejected_telemetry'
  target        TEXT,
  details       JSONB
);
```

Design notes: latency columns on `priority_requests` make the evaluation metrics (Part I) a query rather than a manual exercise. `ambulance_positions` grows quickly at 1 Hz; keep the latest position in memory and write history, and prune or downsample if needed.

---

# PART F — Core algorithms

## F1. Junction identification (not "nearest signal")

Model the map as a graph: junctions are nodes, `road_segments` are directed edges (with polylines) leading into a junction approach.

For each new position of an ambulance:

1. **Smooth heading and speed.** Compute heading from the last N positions (bearing between points), not from a single GPS reading. Use the GPS speed if provided, else derive it from distance/time. Apply an exponential moving average to speed.
2. **Match to a road segment (map matching).** Find candidate segments within a radius (e.g. 30 m of the polyline) whose direction of travel differs from the ambulance heading by less than a tolerance (e.g. 45°). Choose the closest. Keep the previous segment as a bias to avoid flicker (hysteresis).
3. **Upcoming junction = `to_junction` of the matched segment.** If a planned route is known (simulator route or dispatch route), use the next junction on the route instead.
4. **Approach and conflict group:** the segment's `approach_id` identifies which approach of the junction the ambulance will enter, and therefore which conflict group (`NS` or `EW`) needs green.
5. **Distance along the road:** distance from the current projected point to the end of the segment, following the polyline (sum of segment lengths), not the straight line. In the simplest demo geometry, straight-line Haversine to the junction is acceptable if the road is straight; state this.
6. **Reject a junction** the ambulance is moving away from (bearing to junction differs strongly from the heading, or distance is increasing over several samples).

Pseudocode:

```python
def next_junction(amb):
    heading = smoothed_heading(amb.history)
    seg = match_segment(amb.pos, heading, prev=amb.segment)   # radius + heading tolerance + hysteresis
    if seg is None:
        return None                                           # off-map: keep monitoring, no priority
    dist_m = distance_along_polyline(amb.pos, seg)            # to end of segment
    return Upcoming(junction=seg.to_junction, approach=seg.approach_id, distance_m=dist_m)
```

## F2. ETA

```python
def eta_seconds(distance_m, speed_kmh_smoothed, min_speed_kmh=5.0):
    v_ms = max(speed_kmh_smoothed, min_speed_kmh) / 3.6      # km/h -> m/s
    return distance_m / v_ms
```

- Recompute on every position update; keep a moving average of speed to avoid ETA jitter.
- Use a floor speed so a stopped ambulance does not produce an infinite ETA; when the ambulance is nearly stationary, flag "stopped" on the dashboard and hold the request (do not start a transition).
- Record predicted ETA at request time and the actual crossing time to compute **ETA error** for the evaluation.

## F3. Priority decision engine

**Configuration (YAML/JSON, not hard-coded):**

```yaml
thresholds:
  monitor_distance_m: 1000
  prepare_distance_m: 500
  request_distance_m: 500        # < this: generate priority request
  emergency_distance_m: 150      # very close: emergency priority
  request_eta_s: 45              # request when ETA <= this, whichever triggers first
  emergency_eta_s: 12
signal:
  yellow_s: 3
  all_red_s: 2
  min_green_s: 5
  priority_ttl_s: 30             # priority auto-expires if no crossing/refresh
  safety_margin_s: 3
assisted_timeout_s: 10           # escalate if police have not decided
mode: assisted                   # assisted | automatic
```

**Inputs per evaluation:** emergency flag, upcoming junction and approach, distance, ETA, current signal state and remaining time, existing request for this ambulance/junction, other ambulances at this junction, data validity (fresh, plausible).

**Level:**

```text
not emergency, invalid, or moving away        → NONE
distance > monitor_distance_m                 → MONITOR
prepare_distance_m < distance <= monitor      → PREPARE   (alert police, pre-check junction)
distance <= request_distance_m or eta <= request_eta_s → REQUEST
distance <= emergency_distance_m or eta <= emergency_eta_s → EMERGENCY
```

**Rules:**

- Do not create a duplicate request if one is already REQUESTED/APPROVED/ACTIVE for this ambulance and junction.
- **Activation lead time.** Compute when the transition must start so the priority green is on when the ambulance arrives:
  `T_start = ETA − (remaining_current_phase_clearance + yellow_s + all_red_s + safety_margin_s)`.
  If the ambulance's conflict group already has green, no transition is needed: **hold/extend that green** until crossing.
- **Assisted mode:** at REQUEST level, alert police and wait for Approve/Reject. If `assisted_timeout_s` passes with no decision, escalate the alert (repeat, sound, highlight, optional SNS). Priority is activated only on approval.
- **Automatic mode (prototype only):** at REQUEST level, verify data validity (F/H rules), then activate priority automatically and inform police.
- **Reject:** the request becomes REJECTED and the signal stays on the normal cycle. Re-evaluation only creates a new request if the level escalates to EMERGENCY, which is shown to police as a new alert (not an override).
- **Expiry:** an ACTIVE priority always ends by crossing detection or by `priority_ttl_s`, never open-ended.

**Crossing detection:** the ambulance is considered crossed when its projected position passes the junction end of the segment and is then beyond an exit geofence (for example 30 m past the junction), or when a physical sensor triggers (Tier 2 option). A timeout ends the priority if neither occurs.

## F4. Multiple ambulances (documented priority mechanism)

Requests at the same junction are grouped by conflict group (`NS` vs `EW`).

1. **Compatible requests** (same conflict group) are served together by one priority window covering the latest expected crossing (`max(ETA) + buffer`).
2. **Conflicting requests** are ordered by, in this sequence:
   1. Emergency severity level (dispatch/operator-provided: `critical` > `urgent` > `standard`; default `urgent`)
   2. Earlier ETA
   3. Least disruption (the group that already has green wins ties)
   4. Deterministic tie-break on ambulance ID
3. **Serve the first, queue the second.** If the second's ETA falls inside the first's service window, it waits; the system computes the estimated delay and shows it to police. If the second arrives after the first clears, switch after the first crossing and its recovery clearance.
4. **Not first-detected-first.** A later-detected ambulance with a higher severity or sooner ETA can rank ahead.
5. **Starvation guard:** cross traffic is never held longer than `max_hold_s` (e.g. 45 s); if the queue would exceed it, alert police to manage manually.
6. **Police can override the order** from the dashboard; the override is logged.

This is a documented heuristic, not a claim of optimality. State that in the README.

## F5. Traffic signal state machine (identical logic in firmware and in the virtual junction)

```text
NORMAL_CYCLE(phase_i)
   │  priority command for group G (valid, unexpired)
   v
PREEMPT_YELLOW        (current green group shows yellow for yellow_s)
   v
PREEMPT_ALL_RED       (all approaches red for all_red_s)
   v
PRIORITY_GREEN(G)     (group G green; conflicting group red; hold until "crossed" or TTL)
   │  crossed / cancel / TTL expiry
   v
RECOVERY_YELLOW       (group G shows yellow for yellow_s)
   v
RECOVERY_ALL_RED      (all red for all_red_s)
   v
NORMAL_CYCLE(defined resume phase)

Any state ── heartbeat lost / invalid command / internal fault ──> FAULT_SAFE
FAULT_SAFE: finish the current safe transition, then run the normal cycle or a flashing-red/yellow safe pattern.
```

**Safety rules enforced in the firmware (never trust the backend for these):**

1. Never show green to both conflict groups at once.
2. Enforce minimum yellow and all-red times regardless of what the command says.
3. Enforce minimum green before any preemption starts (so the normal cycle is not chopped).
4. Every priority command carries a **TTL** and a sequence number; expired or duplicate commands are ignored.
5. **Heartbeat watchdog:** if no heartbeat/command channel for N seconds, no new priority is started and any active priority ends through the safe recovery sequence.
6. The backend also supports commands `CANCEL_PRIORITY` and `RESUME_NORMAL`.
7. The junction reports every state change (`state` topic) so the dashboard and log always reflect the true signal state, not the intended state.

The **virtual junction** in Tier 1 runs this same state machine (a Python module shared as the reference implementation), so the logic is tested before the hardware exists and the firmware is a port of tested behaviour.

## F6. Detection fusion (Tier 4)

- GPS emergency track + camera detection at the same junction/time → **high confidence**; the request proceeds through the normal engine.
- Camera detection with **no** matching GPS track → **police alert only**, flagged "unverified vehicle"; no signal change.
- GPS emergency with no camera confirmation → normal flow (camera is optional).

---

# PART G — Messaging and API contracts

## G1. MQTT topics (AWS IoT Core)

| Topic | Publisher | Subscriber | Purpose |
|---|---|---|---|
| `ambulance/{id}/telemetry` | ambulance source | backend | position, speed, heading, emergency flag, timestamp |
| `detections/{cameraId}` | CV edge process | backend | ambulance detection event (Tier 4) |
| `junction/{jid}/command` | backend | ESP32 / virtual junction | priority, cancel, resume, config |
| `junction/{jid}/state` | ESP32 / virtual junction | backend | actual signal state and remaining time |
| `junction/{jid}/heartbeat` | ESP32 / virtual junction | backend | liveness every few seconds |

**Telemetry payload:**

```json
{
  "ambulance_id": "A102",
  "lat": 12.9345,
  "lon": 77.6101,
  "speed_kmh": 42.0,
  "heading_deg": 180.0,
  "emergency": true,
  "seq": 1187,
  "ts": "2026-09-20T09:41:12.250Z"
}
```

**Command payload:**

```json
{
  "cmd": "PRIORITY",
  "request_id": "b6f1…",
  "group": "NS",
  "ttl_s": 30,
  "seq": 42,
  "issued_at": "2026-09-20T09:41:13.100Z"
}
```

**IoT policies:** each ambulance thing may publish only to its own `ambulance/{its name}/telemetry`; each junction thing may subscribe only to its own command topic and publish only to its own state/heartbeat topics (use the IoT policy variable for the thing name). The backend has its own certificate with subscribe on `ambulance/+/telemetry`, `junction/+/state|heartbeat`, `detections/+` and publish on `junction/+/command`.

## G2. REST endpoints (FastAPI, Cognito JWT required except health)

| Method | Path | Role | Purpose |
|---|---|---|---|
| POST | `/auth/login` | any | Cognito sign-in, returns tokens |
| GET | `/junctions` | police, admin | junction list with live signal state |
| GET | `/ambulances` | police, admin | active ambulances with latest tracking data |
| GET | `/requests?status=` | police, admin | priority requests |
| POST | `/requests/{id}/approve` | police | approve priority |
| POST | `/requests/{id}/reject` | police | reject priority |
| POST | `/junctions/{id}/resume-normal` | police, admin | manual override to normal |
| GET/PUT | `/config/thresholds` | admin | view or change thresholds |
| GET | `/events/{event_id}` | police, admin | full incident timeline |
| POST | `/sim/start` | admin | start a simulated ambulance run (demo/eval) |
| GET | `/metrics/latency` | admin | latency statistics from the log |
| GET | `/health` | none | liveness |

## G3. WebSocket `/ws` (authenticated with the Cognito token in the first message)

Server pushes: `ambulance_update`, `priority_request`, `request_status`, `signal_state`, `junction_health`, `alert`. Client sends: `approve`, `reject`, `monitor`. The dashboard must update without any page refresh.

---

# PART H — Security and authentication

Prototype-level, but real:

1. **Police and admin login:** Cognito user pool with groups; the backend verifies JWT signature, expiry and group on every REST call and on the WebSocket handshake. Role-based access: only `police`/`admin` can approve, reject or override; only `admin` changes thresholds.
2. **Ambulance authentication:** each ambulance thing has an X.509 certificate with an IoT policy that limits it to its own topic. The phone app authenticates through Cognito as an `ambulance_operator`, and the backend accepts phone telemetry only for the ambulance registered to that operator.
3. **Ambulance ID validation:** telemetry for an unregistered or inactive `ambulance_id` is dropped and written to `audit_log` as `rejected_telemetry`.
4. **Protection against false emergency requests:**
   - Plausibility checks: reject speeds above a configured maximum, position jumps that imply impossible speed, stale timestamps, duplicate/out-of-order `seq`, coordinates off the map.
   - The emergency flag must be set explicitly by the ambulance operator.
   - In assisted mode, a human approves before any signal change.
   - Rate limiting and lockout on repeated invalid requests.
   - In automatic mode (prototype only), all checks above must pass and every activation is logged.
5. **Transport security:** TLS for MQTT (8883) and HTTPS/WSS for browsers.
6. **Logging of signal-control actions:** every approval, rejection, activation, override and state change is written to `audit_log` and `signal_events`.
7. **Least-privilege IAM:** the EC2 instance role has only the IoT, RDS, S3 and CloudWatch permissions it needs; no wildcard actions. Security groups expose only the ports required. RDS is not publicly accessible.
8. **No secrets in the repo:** use environment variables or AWS Secrets Manager/SSM parameters; keep certificates out of git.
9. **Set an AWS Budgets alert on day one.**

---

# PART I — Testing and evaluation

## I1. Scenario tests (automated where possible)

The eight scenarios in C20, plus:

9. **Invalid telemetry:** unregistered ID, impossible speed, stale/duplicated messages → rejected and logged, no priority.
10. **Ambulance moving away:** no priority for a junction it has passed or is leaving.
11. **Police no response:** alert escalates after `assisted_timeout_s`; no unauthorised activation in assisted mode.
12. **Junction offline (heartbeat lost):** dashboard shows the junction as unhealthy, no priority is issued, an active priority ends through the safe sequence.
13. **Broker/backend link lost mid-priority:** priority expires via TTL and firmware returns to normal safely.
14. **Conflict safety test:** a unit/simulation test that runs many random command sequences through the state machine and asserts conflicting groups are never green together and minimum yellow/all-red durations are always respected.
15. **Multiple ambulances:** cases for same group, conflicting groups, differing severity, and starvation-guard trigger.

Write pytest tests for: ETA and unit conversion, junction identification (heading and hysteresis), threshold logic, duplicate-request prevention, state machine safety, authorisation on endpoints.

## I2. Evaluation study (this is what makes the project measurable)

**Method:** run the simulator repeatedly through the same route on the virtual junction (and on hardware for a smaller number of runs), in two configurations:

- **Baseline (conventional signal):** the ambulance arrives at random points in the normal cycle and waits for its green.
- **Proposed system:** assisted (with a scripted approval delay) and automatic modes.

Use at least 30 runs per configuration with randomised arrival phase; report mean, median, spread.

| Metric | How it is measured |
|---|---|
| Ambulance detection accuracy | GPS: fraction of emergency runs identified. CV: precision, recall, mAP on a held-out image set (Tier 4) |
| GPS update frequency | intervals between telemetry messages (target ~1 Hz), plus loss/jitter |
| ETA accuracy | predicted ETA at request time vs actual crossing time; report mean absolute error |
| Detection-to-alert latency | `t_alert − t_first_detect` |
| Alert-to-signal latency | `t_signal_ack − t_decision` (approval → command → junction acknowledgement) |
| Ambulance waiting time | time the ambulance is stopped or delayed at the junction, baseline vs proposed |
| Normal traffic waiting time | added delay to cross traffic per priority event, baseline vs proposed |
| Signal transition time | duration of preempt and recovery sequences |
| Priority success rate | fraction of runs where the ambulance found green on arrival without stopping |
| Dashboard response time | telemetry received → dashboard rendered (timestamped in the browser) |

**Output:** tables and matplotlib graphs (box plots of ambulance wait, bar chart of latencies, ETA error histogram) in `eval/results/` and summarised in the README. **Report results as measured, including failures.** They are simulation results and must be labelled as such.

## I3. Final end-to-end checks before submitting

- Fresh browser, login as police, full approve flow on the **deployed** stack.
- Full reject flow and the timeout/escalation flow.
- Phone geolocation ambulance visible on the map (HTTPS).
- Junction offline test behaves safely.
- The demo works from a clean start with no local process other than the simulator/ESP32/camera devices.

---

# PART J — Build plan, repository and agent instructions

## J1. Instructions for the building agent

1. Read this whole file first. Build a **vertical slice** first: simulator → IoT Core → backend → engine → dashboard → virtual junction → database. Then deploy it. Then everything else in tier order.
2. **Do not add features** outside the tiers. If something seems missing, say so and let the humans decide.
3. **No agent, chatbot, RAG or LLM in the core path.** Do not add AWS services not listed in Part D without asking; every service needs a stated reason.
4. **Safety logic is deterministic and tested.** The state machine, priority engine and eligibility of any command never depend on an LLM or on unvalidated input.
5. The firmware safety rules in F5 are non-negotiable, and the virtual junction must implement the same state machine.
6. All thresholds live in configuration, not in code.
7. Keep every change small, committed, and keep the deployed stack working after the first deployment.
8. Record every non-obvious decision in `DECISIONS.md` (one line each). The two humans must be able to defend every decision in an interview.
9. Never present the project as controlling real traffic infrastructure. Repeat the C27 limitation in the README and UI footer.

## J2. Build plan (about 36 hours, two people)

Roles are A and B; swap as suits your strengths. Gates are hard checkpoints. **If a gate is missed, do not start the next tier; fix or cut.**

**Block 0 — Setup and gates (first ~2 hours)**
- Both: AWS account, Builder Center verification, credits, **Budgets alert**, one region, repo, `DECISIONS.md`. Confirm the submission cutoff.
- A: create IoT Core things and certificates for one ambulance and the backend; confirm a publish/subscribe round trip from the laptop.
- B: scaffold the frontend (Leaflet + OSM showing one junction); pick the demo junction and define its road segments and approaches in a seed file.
- Gate 0: IoT round trip works. If not within ~2 hours, use a local Mosquitto broker to keep building and return to IoT Core in Block 3.

**Block 1 — Core engine (~5 hours)**
- A: FastAPI skeleton, MQTT consumer, junction identification, ETA, priority engine with configurable thresholds, unit tests.
- B: GPS simulator (replays a route at configurable speed and 1 Hz), virtual junction implementing the F5 state machine, plus conflict-safety test.
- Gate 1: the simulator drives an ambulance; logs show correct upcoming junction, distance, ETA, request level, and a valid signal sequence on the virtual junction.

**Block 2 — Dashboard and persistence (~5 hours)**
- A: PostgreSQL schema, event/audit logging, REST endpoints, WebSocket hub, approve/reject flow.
- B: dashboard (map, ambulance marker and route, alert panel, Approve/Reject/Monitor, junction signal display, event log).
- Gate 2: complete flow works locally: run → alert → approve → signal changes → crossing → normal restored → event stored.

**Block 3 — AWS deployment and security (~4 hours)**
- A: RDS, EC2 (Docker), CloudFront in front, CloudWatch logs and latency metrics.
- B: Cognito user pool and groups, login screen, JWT verification, role checks, IoT policies.
- Gate 3: the whole Tier 1 flow works on the **deployed** stack from a clean browser. From here on, only bug fixes and the next tiers.

**Block 4 — ESP32 junction (Tier 2, ~3–4 hours, conditional)**
- Start only if Gate 3 is passed and the hardware is available.
- B: wire LEDs, port the F5 state machine to firmware with the safety rules, connect over MQTT (fallbacks in D5).
- A: add heartbeat monitoring, latency instrumentation, fail-safe test.
- Gate 4: physical LEDs follow the dashboard flow, including a heartbeat-loss test. If not passed by the time limit, drop it and keep the virtual junction for the demo.

**Block 5 — Measurement and robustness (Tier 3, ~3 hours)**
- Evaluation harness, baseline vs proposed runs, graphs; multiple-ambulance handling; phone geolocation app over HTTPS; false-request checks.
- Gate 5: results tables/graphs exist and are in the README.

**Block 6 — Computer vision (Tier 4, only if time clearly remains)**
- YOLO ambulance detector with OpenCV, events over MQTT, frames to S3, fusion rule F6. Optional density counts.
- If the time is short, describe it as future work and leave it out of the demo. A half-working detector hurts more than an honest omission.

**Block 7 — Freeze, README, demo, submit (last ≥4 hours before cutoff)**
- Feature freeze. README, architecture diagram, evaluation results, limitations, real learnings. Record the video (two takes). Submit early.

## J3. Repository layout

```text
ambulance-priority/
├── README.md              # problem, architecture, AWS roles, results, safety limitation, learnings
├── DECISIONS.md
├── config/
│   └── thresholds.yaml
├── backend/               # FastAPI
│   ├── app/main.py
│   ├── app/mqtt_client.py
│   ├── app/tracking.py        # smoothing, map matching, junction identification
│   ├── app/eta.py
│   ├── app/priority_engine.py
│   ├── app/multi_ambulance.py
│   ├── app/signal_fsm.py      # reference state machine (shared logic)
│   ├── app/security.py        # Cognito JWT, plausibility checks
│   ├── app/db.py, models.py
│   └── Dockerfile
├── frontend/              # HTML/CSS/JS + Leaflet
│   ├── index.html (police dashboard)
│   └── ambulance.html (phone geolocation app)
├── simulator/             # ambulance route replay
├── firmware/              # ESP32 (Tier 2)
├── cv/                    # YOLO + OpenCV (Tier 4)
├── db/schema.sql, seed.sql
├── eval/                  # harness, results, graphs
├── tests/
├── infra/                 # notes/templates for IoT policies, IAM, CloudFront
└── docs/architecture.png
```

---

# PART K — Demo and submission

## K1. Three-minute demo script

The video must show the working product. Record on the **deployed** stack.

| Time | Content |
|---|---|
| 0:00–0:25 | The problem in plain words: an ambulance, a signal on a fixed cycle, no awareness. Who it is for: control-room police and ambulance drivers. State clearly this is a prototype. |
| 0:25–1:45 | The working flow on the dashboard: ambulance starts moving → tracked on the map → junction identified, distance and ETA shown → Prepare then Request → police approves → signal transitions safely (yellow, all-red, priority green) → ambulance crosses → normal cycle restored. Show the ESP32 junction if Tier 2 works, or the virtual junction otherwise. |
| 1:45–2:10 | Edge cases: a rejected request and a junction/heartbeat failure staying safe. If multi-ambulance is done, show it briefly. |
| 2:10–2:40 | Measured results: baseline vs proposed waiting time graph, latencies. Label them as simulation results. |
| 2:40–3:00 | AWS architecture (IoT Core, EC2, RDS, Cognito, CloudFront, CloudWatch, S3) with one sentence on why each is there, plus impact and what the team learned. |

Rehearse once with a timer. Keep a backup screen recording of the full flow in case live conditions fail during recording.

## K2. Submission checklist

- [ ] Deployed on AWS and working from a clean browser
- [ ] Public repo with README, architecture diagram, `DECISIONS.md`
- [ ] README states: problem, users, AWS service roles, evaluation results (as measured), safety limitation, known limitations, real learnings
- [ ] 3-minute demo video recorded and uploaded
- [ ] Both team members can explain every component
- [ ] AWS Budgets alert set, no resources left running unnecessarily after judging
- [ ] Submitted well before the cutoff

## K3. Learning section (write only what actually happened)

Candidates: first use of AWS IoT Core with device certificates and least-privilege policies; MQTT plus WebSocket real-time architecture; CloudFront with WebSockets; Cognito role-based access; building a safety-critical state machine and testing it; ESP32 TLS/MQTT; measuring latency end to end; YOLO fine-tuning (only if done).

## K4. Interview defence questions (both teammates should answer)

1. Why IoT Core and MQTT rather than plain HTTP polling? Why WebSocket for the dashboard?
2. How do you know which junction the ambulance is heading to? What happens with GPS noise or when it turns?
3. What happens if the network drops while a priority is active? Where does the safety logic live and why?
4. Why does the firmware enforce the interlock instead of the backend?
5. How do you stop a false emergency request or a spoofed ambulance?
6. Why assisted mode by default? What is the trade-off with approval latency?
7. How does the multi-ambulance rule work, and where can it fail?
8. What did the evaluation show, and what are its limits (simulation, not real roads)?
9. How would this scale to many junctions and ambulances? What would change first?
10. What would real deployment require? (See C27.)

---

# PART L — Risks and fallbacks

| Risk | Likelihood | Mitigation / fallback |
|---|---|---|
| Scope too large for the time | Very high | Tiers and gates in Part B3 and J2; cut YOLO and hardware before cutting Tier 1 |
| ESP32 TLS/IoT Core connection takes too long | High | Fallbacks in D5; keep the virtual junction as the demo path |
| Hardware or Wi-Fi fails during recording | Medium | Backup recording; virtual junction; phone hotspot tested in advance |
| HTTPS/WSS problems (mixed content, CloudFront WebSocket config) | Medium | Test in Block 3, not on demo day; ALB + ACM alternative |
| Geolocation blocked because the page is not HTTPS | Medium | Serve through CloudFront; test on the phone early |
| GPS noise causes wrong junction/ETA | Medium | Heading smoothing, map matching with hysteresis, plausibility filters |
| Approval latency makes assisted mode too slow | Medium | Alert at Prepare stage, configurable lead time, escalation, automatic mode in the prototype only |
| Unsafe signal behaviour in a failure | Low (must be zero) | Firmware interlock, TTL, heartbeat watchdog, safety simulation test |
| YOLO false positives or poor dataset | High | Secondary signal only; never triggers signal change alone |
| Unsourced impact claims | Medium | Claim only what was measured; label simulation results |
| AWS cost surprise | Low-Medium | Budgets alert; small instance sizes; shut down after judging |
| Feature creep | High | Part B3 is the contract; new ideas go to "Future work" |

---

# Definition of done

A person who has never seen the project can log in as police on the deployed URL and watch an ambulance run from start to finish: it is tracked, the correct junction, distance and ETA are shown, a priority request appears, the police approve, the signal changes safely and gives priority, the ambulance crosses, normal operation resumes, and the full event is stored and visible. The README contains the architecture, the measured baseline-vs-proposed results, the safety limitation and the real learnings, and a three-minute demo video was submitted before the cutoff.
