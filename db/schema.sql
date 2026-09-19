-- ============================================================================
-- Intelligent Ambulance Priority and Real-Time Traffic Signal Management
-- PostgreSQL / SQLite Compatible Schema
-- ============================================================================

CREATE TABLE IF NOT EXISTS users (
    user_id       TEXT PRIMARY KEY,
    cognito_sub   TEXT UNIQUE NOT NULL,
    name          TEXT NOT NULL,
    role          TEXT NOT NULL CHECK (role IN ('admin', 'police', 'ambulance_operator')),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ambulances (
    ambulance_id     TEXT PRIMARY KEY,
    vehicle_number   TEXT UNIQUE NOT NULL,
    operator_user_id TEXT REFERENCES users(user_id),
    iot_thing_name   TEXT UNIQUE,
    active           BOOLEAN DEFAULT 1
);

CREATE TABLE IF NOT EXISTS junctions (
    junction_id    TEXT PRIMARY KEY,
    name           TEXT NOT NULL,
    latitude       REAL NOT NULL,
    longitude      REAL NOT NULL,
    iot_thing_name TEXT UNIQUE,
    config         TEXT NOT NULL -- JSON encoded config (yellow_s, all_red_s, phases)
);

CREATE TABLE IF NOT EXISTS junction_approaches (
    approach_id   TEXT PRIMARY KEY,
    junction_id   TEXT NOT NULL REFERENCES junctions(junction_id),
    name          TEXT NOT NULL,
    bearing_deg   REAL NOT NULL,
    green_group   TEXT NOT NULL CHECK (green_group IN ('NS', 'EW'))
);

CREATE TABLE IF NOT EXISTS road_segments (
    segment_id    TEXT PRIMARY KEY,
    from_junction TEXT REFERENCES junctions(junction_id),
    to_junction   TEXT NOT NULL REFERENCES junctions(junction_id),
    polyline      TEXT NOT NULL, -- JSON array of [lat, lon]
    length_m      REAL NOT NULL,
    approach_id   TEXT NOT NULL REFERENCES junction_approaches(approach_id)
);

CREATE TABLE IF NOT EXISTS ambulance_positions (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    ambulance_id TEXT NOT NULL REFERENCES ambulances(ambulance_id),
    ts           TIMESTAMP NOT NULL,
    latitude     REAL NOT NULL,
    longitude    REAL NOT NULL,
    speed_kmh    REAL,
    heading_deg  REAL,
    emergency    BOOLEAN NOT NULL,
    source       TEXT CHECK (source IN ('simulator', 'phone', 'camera'))
);

CREATE TABLE IF NOT EXISTS emergency_events (
    event_id     TEXT PRIMARY KEY,
    ambulance_id TEXT NOT NULL REFERENCES ambulances(ambulance_id),
    started_at   TIMESTAMP NOT NULL,
    ended_at     TIMESTAMP,
    mode         TEXT CHECK (mode IN ('assisted', 'automatic'))
);

CREATE TABLE IF NOT EXISTS priority_requests (
    request_id      TEXT PRIMARY KEY,
    event_id        TEXT REFERENCES emergency_events(event_id),
    ambulance_id    TEXT NOT NULL REFERENCES ambulances(ambulance_id),
    junction_id     TEXT NOT NULL REFERENCES junctions(junction_id),
    approach_id     TEXT NOT NULL REFERENCES junction_approaches(approach_id),
    distance_m      REAL,
    eta_s           REAL,
    priority_level  TEXT CHECK (priority_level IN ('MONITOR', 'PREPARE', 'REQUEST', 'EMERGENCY')),
    status          TEXT CHECK (status IN ('REQUESTED', 'APPROVED', 'REJECTED', 'ACTIVE', 'COMPLETED', 'EXPIRED', 'CANCELLED')),
    decided_by      TEXT REFERENCES users(user_id),
    -- Latency Instrumentation
    t_first_detect  TIMESTAMP,
    t_alert         TIMESTAMP,
    t_decision      TIMESTAMP,
    t_command_sent  TIMESTAMP,
    t_signal_ack    TIMESTAMP,
    t_crossed       TIMESTAMP,
    t_normal_restored TIMESTAMP
);

CREATE TABLE IF NOT EXISTS signal_events (
    event_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    junction_id    TEXT NOT NULL REFERENCES junctions(junction_id),
    request_id     TEXT REFERENCES priority_requests(request_id),
    previous_state TEXT NOT NULL,
    new_state      TEXT NOT NULL,
    reason         TEXT NOT NULL,
    ts             TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS detection_events (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    camera_id            TEXT NOT NULL,
    confidence           REAL NOT NULL,
    matched_ambulance_id TEXT REFERENCES ambulances(ambulance_id),
    frame_s3_key         TEXT,
    ts                   TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_log (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    ts            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actor_type    TEXT NOT NULL,
    actor_id      TEXT NOT NULL,
    action        TEXT NOT NULL,
    target        TEXT,
    details       TEXT -- JSON encoded
);
