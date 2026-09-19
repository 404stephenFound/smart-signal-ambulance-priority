import httpx
import json

def test_live_site():
    base_url = "http://127.0.0.1:8000"
    with httpx.Client(base_url=base_url, timeout=5.0) as client:
        print("\n--- 1. Testing Health API ---")
        res = client.get("/health")
        print("Health Status:", res.status_code, res.json())
        assert res.status_code == 200

        print("\n--- 2. Testing Police Dashboard HTML ---")
        res_dash = client.get("/")
        print("Dashboard Status:", res_dash.status_code, f"HTML Size: {len(res_dash.text)} bytes")
        assert res_dash.status_code == 200
        assert "Emergency Corridor Priority System" in res_dash.text
        assert "id=\"map\"" in res_dash.text

        print("\n--- 3. Testing Ambulance Driver Web App ---")
        res_amb = client.get("/ambulance")
        print("Ambulance App Status:", res_amb.status_code, f"HTML Size: {len(res_amb.text)} bytes")
        assert res_amb.status_code == 200
        assert "Ambulance Operator HUD" in res_amb.text

        print("\n--- 4. Testing Junctions API ---")
        res_junc = client.get("/junctions")
        juncs = res_junc.json()
        print("Junctions Count:", len(juncs), "First Junction:", juncs[0]["name"], "| State:", juncs[0]["state"]["state"])
        assert res_junc.status_code == 200

        print("\n--- 5. Ingesting Ambulance Telemetry ---")
        payload = {
            'ambulance_id': 'A102',
            'lat': 12.9760,
            'lon': 77.6074,
            'speed_kmh': 45.0,
            'heading_deg': 180.0,
            'emergency': True,
            'seq': 1,
            'source': 'simulator'
        }
        res_tel = client.post("/telemetry", json=payload)
        tel_data = res_tel.json()
        print("Telemetry Status:", tel_data['status'], "| Next Junction:", tel_data['active_data']['upcoming']['junction_name'])
        assert res_tel.status_code == 200

        print("\n--- 6. Checking Priority Requests ---")
        res_reqs = client.get("/requests")
        reqs = res_reqs.json()
        print(f"Requests Active: {len(reqs)} | Level: {reqs[0]['priority_level']} | Status: {reqs[0]['status']}")
        assert len(reqs) > 0

        print("\n--- 7. Simulating Police Approval ---")
        req_id = reqs[0]['request_id']
        if reqs[0]['status'] == 'REQUESTED':
            res_app = client.post(f"/requests/{req_id}/approve?group=NS", headers={'Authorization': 'Bearer token-police'})
            app_data = res_app.json()
            print("Approval Result:", app_data['status'], "| Command Issued:", app_data['command']['cmd'], "Group:", app_data['command']['group'])
            assert res_app.status_code == 200
        else:
            print("Request already in ACTIVE status from prior test run.")
            assert reqs[0]['status'] == 'ACTIVE'

    print("\n>>> ALL LIVE END-TO-END WEBSITE TESTS PASSED SUCCESSFULLY! <<<\n")

if __name__ == "__main__":
    test_live_site()
