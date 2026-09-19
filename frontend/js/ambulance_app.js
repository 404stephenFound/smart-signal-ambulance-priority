// Mobile Ambulance Driver Web App Logic
let isEmergency = false;
let geoWatchId = null;
let telemetrySeq = 0;
const AMBULANCE_ID = "A102";

function toggleEmergencyMode() {
  isEmergency = !isEmergency;
  const btn = document.getElementById('toggle-emergency-btn');
  const beacon = document.getElementById('beacon-status');

  if (isEmergency) {
    btn.className = 'emergency-btn active';
    btn.innerHTML = '<span>🚨 CODE-RED PRIORITY ACTIVE</span>';
    beacon.innerText = 'TRANSMITTING 1Hz';
    beacon.style.color = '#34d399';
    startGeolocationTracking();
  } else {
    btn.className = 'emergency-btn inactive';
    btn.innerHTML = '<span>🚨 EMERGENCY MODE: OFF</span>';
    beacon.innerText = 'BEACON IDLE';
    beacon.style.color = '#38bdf8';
    stopGeolocationTracking();
  }
}

function startGeolocationTracking() {
  if ("geolocation" in navigator) {
    geoWatchId = navigator.geolocation.watchPosition(
      (pos) => {
        sendAmbulanceTelemetry(pos.coords.latitude, pos.coords.longitude, (pos.coords.speed || 12.0) * 3.6, pos.coords.heading || 180.0);
      },
      (err) => {
        console.warn("Geolocation fallback to simulation: ", err.message);
        // Fallback simulated step if browser blocks GPS permissions
        simulateMobileStep();
      },
      { enableHighAccuracy: true, maximumAge: 1000, timeout: 5000 }
    );
  } else {
    simulateMobileStep();
  }
}

function stopGeolocationTracking() {
  if (geoWatchId !== null) {
    navigator.geolocation.clearWatch(geoWatchId);
    geoWatchId = null;
  }
}

async function sendAmbulanceTelemetry(lat, lon, speedKmh, heading) {
  telemetrySeq++;
  const payload = {
    ambulance_id: AMBULANCE_ID,
    lat: lat,
    lon: lon,
    speed_kmh: Math.round(speedKmh),
    heading_deg: Math.round(heading),
    emergency: isEmergency,
    seq: telemetrySeq,
    source: "phone"
  };

  document.getElementById('hud-speed').innerText = `${Math.round(speedKmh)} km/h`;

  try {
    const res = await fetch('/telemetry', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.active_data && data.active_data.upcoming) {
      const up = data.active_data.upcoming;
      document.getElementById('hud-junction').innerText = up.junction_name;
      document.getElementById('hud-distance').innerText = `${up.distance_m} m`;
      document.getElementById('hud-eta').innerText = `${up.eta_s} s`;
    }
    if (data.active_data && data.active_data.active_request && data.active_data.active_request.status === 'ACTIVE') {
      document.getElementById('corridor-status-box').style.display = 'block';
    } else {
      document.getElementById('corridor-status-box').style.display = 'none';
    }
  } catch (e) {
    console.error("Telemetry transmit failed:", e);
  }
}

// Fallback mobile stepping simulation
let simStep = 0;
function simulateMobileStep() {
  if (!isEmergency) return;
  const coords = [
    [12.9820, 77.6074], [12.9790, 77.6074], [12.9760, 77.6074],
    [12.9740, 77.6074], [12.9738, 77.6074], [12.9725, 77.6074]
  ];
  const pt = coords[simStep % coords.length];
  sendAmbulanceTelemetry(pt[0], pt[1], 45.0, 180.0);
  simStep++;
  setTimeout(simulateMobileStep, 1500);
}
