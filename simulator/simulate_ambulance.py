import time
import argparse
import json
import urllib.request
import urllib.error

# Bangalore Junction JN-04 Corridors
ROUTES = {
    "north": {
        "bearing": 180.0,
        "name": "North (Cubbon Road to JN-04)",
        "coords": [
            (12.9820, 77.6074), (12.9805, 77.6074), (12.9790, 77.6074),
            (12.9775, 77.6074), (12.9760, 77.6074), (12.9748, 77.6074),
            (12.9740, 77.6074), (12.9738, 77.6074), (12.9725, 77.6074)
        ]
    },
    "west": {
        "bearing": 90.0,
        "name": "West (MG Road West to JN-04)",
        "coords": [
            (12.9738, 77.5980), (12.9738, 77.6000), (12.9738, 77.6025),
            (12.9738, 77.6045), (12.9738, 77.6060), (12.9738, 77.6074),
            (12.9738, 77.6090)
        ]
    },
    "south": {
        "bearing": 0.0,
        "name": "South (Brigade Road to JN-04)",
        "coords": [
            (12.9650, 77.6074), (12.9680, 77.6074), (12.9710, 77.6074),
            (12.9730, 77.6074), (12.9738, 77.6074), (12.9750, 77.6074)
        ]
    }
}

def run_simulation(
    server_url: str = "http://localhost:8000",
    ambulance_id: str = "A102",
    route_name: str = "north",
    speed_kmh: float = 48.0,
    interval_s: float = 1.0,
    emergency: bool = True
):
    route_data = ROUTES.get(route_name, ROUTES["north"])
    coords = route_data["coords"]
    bearing = route_data["bearing"]

    print(f"\n=======================================================")
    print(f"🚑 Launching GPS Simulator for Ambulance {ambulance_id}")
    print(f"📍 Route: {route_data['name']}")
    print(f"⚡ Speed: {speed_kmh} km/h | Interval: {interval_s}s | Emergency: {emergency}")
    print(f"=======================================================\n")

    for seq, (lat, lon) in enumerate(coords, start=1):
        payload = {
            "ambulance_id": ambulance_id,
            "lat": lat,
            "lon": lon,
            "speed_kmh": speed_kmh,
            "heading_deg": bearing,
            "emergency": emergency,
            "seq": seq,
            "source": "simulator"
        }

        try:
            req = urllib.request.Request(
                f"{server_url}/telemetry",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                active = res_data.get("active_data", {})
                upcoming = active.get("upcoming")
                if upcoming:
                    print(f"[{seq}/{len(coords)}] Lat: {lat:.4f}, Lon: {lon:.4f} -> Next: {upcoming['junction_name']} | Dist: {upcoming['distance_m']}m | ETA: {upcoming['eta_s']}s")
                else:
                    print(f"[{seq}/{len(coords)}] Lat: {lat:.4f}, Lon: {lon:.4f} -> Monitoring...")
        except Exception as e:
            print(f"[{seq}/{len(coords)}] Telemetry transmit error: {e}")

        time.sleep(interval_s)

    print("\n✅ Simulation route replay finished.\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Emergency Ambulance GPS Telemetry Simulator")
    parser.add_argument("--server", default="http://localhost:8000", help="FastAPI backend URL")
    parser.add_argument("--amb", default="A102", help="Ambulance ID")
    parser.add_argument("--route", default="north", choices=["north", "west", "south"], help="Route corridor")
    parser.add_argument("--speed", type=float, default=48.0, help="Vehicle speed in km/h")
    parser.add_argument("--interval", type=float, default=1.0, help="Telemetry interval in seconds")
    parser.add_argument("--non-emergency", action="store_true", help="Set emergency to false")
    args = parser.parse_args()

    run_simulation(
        server_url=args.server,
        ambulance_id=args.amb,
        route_name=args.route,
        speed_kmh=args.speed,
        interval_s=args.interval,
        emergency=not args.non_emergency
    )
