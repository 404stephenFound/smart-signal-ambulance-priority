import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = os.environ.get("DATABASE_PATH", "traffic_system.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "db", "schema.sql")
SEED_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "db", "seed.sql")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize SQLite database with schema and seed data."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Run schema if exists
    if os.path.exists(SCHEMA_PATH):
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            cursor.executescript(f.read())
            
    # Run seed if junctions table is empty
    cursor.execute("SELECT COUNT(*) as cnt FROM junctions")
    if cursor.fetchone()["cnt"] == 0:
        if os.path.exists(SEED_PATH):
            with open(SEED_PATH, "r", encoding="utf-8") as f:
                cursor.executescript(f.read())
                
    conn.commit()
    conn.close()

def log_audit(actor_type: str, actor_id: str, action: str, target: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO audit_log (actor_type, actor_id, action, target, details)
               VALUES (?, ?, ?, ?, ?)""",
            (actor_type, actor_id, action, target, json.dumps(details or {}))
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB Error] Audit logging failed: {e}")

def save_ambulance_position(data: Dict[str, Any]):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO ambulance_positions (ambulance_id, ts, latitude, longitude, speed_kmh, heading_deg, emergency, source)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                data["ambulance_id"],
                data.get("ts", datetime.utcnow().isoformat()),
                data["lat"],
                data["lon"],
                data.get("speed_kmh", 0.0),
                data.get("heading_deg"),
                1 if data.get("emergency", True) else 0,
                data.get("source", "simulator")
            )
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB Error] Position save failed: {e}")

def log_signal_event(junction_id: str, request_id: Optional[str], previous_state: str, new_state: str, reason: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO signal_events (junction_id, request_id, previous_state, new_state, reason, ts)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (junction_id, request_id, previous_state, new_state, reason, datetime.utcnow().isoformat())
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB Error] Signal event log failed: {e}")
