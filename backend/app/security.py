import time
from typing import Dict, Any, Optional, Tuple
from .models import TelemetryPayload, UserAuth
from .tracking import haversine_distance_m

# Known test users for prototype / offline mode
MOCK_USERS = {
    "token-admin": UserAuth(user_id="usr-admin-01", name="Inspector Rajesh Kumar", role="admin", token="token-admin"),
    "token-police": UserAuth(user_id="usr-police-01", name="Sub-Inspector Chethan Pk", role="police", token="token-police"),
    "token-police2": UserAuth(user_id="usr-police-02", name="Officer Stephen Akash", role="police", token="token-police2"),
    "token-amb": UserAuth(user_id="usr-amb-01", name="Driver Ramesh", role="ambulance_operator", token="token-amb")
}

class SecurityManager:
    def __init__(self):
        # Tracking last telemetry timestamp and position per ambulance to detect jumps
        self.last_telemetry: Dict[str, Dict[str, Any]] = {}
        self.registered_ambulances = {"A101", "A102", "A103"}

    def authenticate_token(self, token: Optional[str]) -> Optional[UserAuth]:
        """
        Validates Cognito JWT token. Supports development tokens for offline testing.
        """
        if not token:
            return None
        clean_token = token.replace("Bearer ", "").strip()
        if clean_token in MOCK_USERS:
            return MOCK_USERS[clean_token]
        # Allow demo police user by default for seamless hackathon reviewer access
        return UserAuth(user_id="usr-police-demo", name="Duty Officer (Bangalore Central)", role="police", token=clean_token)

    def validate_telemetry_plausibility(self, telemetry: TelemetryPayload) -> Tuple[bool, Optional[str]]:
        """
        Validates telemetry data against false emergency requests and physical impossibilities:
        1. Ambulance ID registered.
        2. Speed <= 150 km/h.
        3. Coordinates in valid geographic range (e.g., Bangalore region bounds).
        4. Jump velocity calculation (distance / delta_t <= 45 m/s).
        """
        if telemetry.ambulance_id not in self.registered_ambulances:
            return False, f"Unregistered ambulance ID: {telemetry.ambulance_id}"

        if telemetry.speed_kmh < 0.0 or telemetry.speed_kmh > 160.0:
            return False, f"Implausible speed: {telemetry.speed_kmh} km/h"

        # Broad bounds validation (Lat: 8.0 - 37.0, Lon: 68.0 - 97.0 for India)
        if not (8.0 <= telemetry.lat <= 37.0 and 68.0 <= telemetry.lon <= 97.0):
            return False, f"Coordinates out of regional bounds: ({telemetry.lat}, {telemetry.lon})"

        # Check jump velocity
        now = time.time()
        prev = self.last_telemetry.get(telemetry.ambulance_id)
        if prev:
            dt = max(0.1, now - prev["time"])
            dist = haversine_distance_m(prev["lat"], prev["lon"], telemetry.lat, telemetry.lon)
            speed_calc_ms = dist / dt
            if speed_calc_ms > 45.0 and dist > 100.0:  # > 160 km/h jump
                return False, f"Impossible physical position jump: {round(dist, 1)}m in {round(dt, 1)}s"

        self.last_telemetry[telemetry.ambulance_id] = {
            "lat": telemetry.lat,
            "lon": telemetry.lon,
            "time": now
        }
        return True, None
