// Mobile Ambulance Driver Web App Logic
let isEmergency = false;
let geoWatchId = null;
let simInterval = null;
let telemetrySeq = 0;
let activeMode = 'sim'; // 'sim' or 'gps'
const AMBULANCE_ID = "A102";

// Route coordinates approaching JN-04 from North (Cubbon Road)
const SIM_ROUTE = [
  { lat: 12.9830, lon: 77.6074, speed: 52, heading: 180 },
  { lat: 12.9815, lon: 77.6074, speed: 55, heading: 180 },
  { lat: 12.9800, lon: 77.6074, speed: 50, heading: 180 },
  { lat: 12.9785, lon: 77.6074, speed: 48, heading: 180 },
  { lat: 12.9770, lon: 77.6074, speed: 45, heading: 180 },
  { lat: 12.9755, lon: 77.6074, speed: 42, heading: 180 },
  { lat: 12.9745, lon: 77.6074, speed: 38, heading: 180 },
  { lat: 12.9738, lon: 77.6074, speed: 35, heading: 180 }, // Junction center
  { lat: 12.9725, lon: 77.6074, speed: 45, heading: 180 }, // Passed
  { lat: 12.9710, lon: 77.6074, speed: 50, heading: 180 }
];
let simIndex = 0;

function setTrackingMode(mode) {
  activeMode = mode;
  document.getElementById('mode-sim-btn').className = mode === 'sim' ? 'mode-btn active' : 'mode-btn';
  document.getElementById('mode-gps-btn').className = mode === 'gps' ? 'mode-btn active' : 'mode-btn';
  
  if (isEmergency) {
    stopTracking();
    startTracking();
  }
}

function toggleEmergencyMode() {
  isEmergency = !isEmergency;
  const btn = document.getElementById('toggle-emergency-btn');
  const beacon = document.getElementById('beacon-status');

  if (isEmergency) {
    btn.className = 'emergency-btn active';
    btn.innerHTML = '<span>🚨 CODE-RED TRANSMITTING</span>';
    beacon.innerText = 'TRANSMITTING 1Hz';
    beacon.style.color = '#34d399';
    startTracking();
  } else {
    btn.className = 'emergency-btn inactive';
    btn.innerHTML = '<span>🚨 START EMERGENCY PRIORITY</span>';
    beacon.innerText = 'BEACON IDLE';
    beacon.style.color = '#38bdf8';
    stopTracking();
  }
}

function startTracking() {
  if (activeMode === 'gps') {
    startRealGPS();
  } else {
    startSimulation();
  }
}

function stopTracking() {
  if (geoWatchId !== null) {
    navigator.geolocation.clearWatch(geoWatchId);
    geoWatchId = null;
  }
  if (simInterval !== null) {
    clearInterval(simInterval);
    simInterval = null;
  }
}

function startRealGPS() {
  if ("geolocation" in navigator) {
    document.getElementById('coord-mode-tag').innerText = "Live Phone GPS";
    geoWatchId = navigator.geolocation.watchPosition(
      (pos) => {
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;
        const speed = pos.coords.speed ? (pos.coords.speed * 3.6) : 35.0;
        const heading = pos.coords.heading || 180.0;
        updateCoordDisplay(lat, lon);
        sendAmbulanceTelemetry(lat, lon, speed, heading, "real_gps");
      },
      (err) => {
        console.warn("GPS Permission or signal error:", err.message);
        document.getElementById('coord-mode-tag').innerText = "GPS Error — Switching to Demo Route";
        setTrackingMode('sim');
      },
      { enableHighAccuracy: true, maximumAge: 1000, timeout: 5000 }
    );
  } else {
    alert("Geolocation is not supported by your browser. Using simulated route.");
    setTrackingMode('sim');
  }
}

function startSimulation() {
  document.getElementById('coord-mode-tag').innerText = "Demo Corridor Drive (Bangalore)";
  simIndex = 0;
  runSimStep();
  simInterval = setInterval(runSimStep, 1000);
}

function runSimStep() {
  if (!isEmergency) return;
  const pt = SIM_ROUTE[simIndex % SIM_ROUTE.length];
  updateCoordDisplay(pt.lat, pt.lon);
  sendAmbulanceTelemetry(pt.lat, pt.lon, pt.speed, pt.heading, "demo_sim");
  simIndex++;
}

function updateCoordDisplay(lat, lon) {
  const elem = document.getElementById('hud-coords');
  if (elem) {
    elem.innerText = `${lat.toFixed(5)}, ${lon.toFixed(5)}`;
  }
}

async function sendAmbulanceTelemetry(lat, lon, speedKmh, heading, srcType) {
  telemetrySeq++;
  const payload = {
    ambulance_id: AMBULANCE_ID,
    lat: lat,
    lon: lon,
    speed_kmh: Math.round(speedKmh),
    heading_deg: Math.round(heading),
    emergency: isEmergency,
    seq: telemetrySeq,
    source: srcType || "phone"
  };

  document.getElementById('hud-speed').innerText = `${Math.round(speedKmh)} km/h`;
  document.getElementById('hud-packets').innerText = `#${telemetrySeq}`;

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
