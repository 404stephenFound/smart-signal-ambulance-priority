// Intelligent Traffic Priority & Police Control Dashboard Logic
// Team infinity — First Commit Hackathon

let map;
let junctionMarkers = {};
let ambulanceMarkers = {};
let routePolylines = {};
let ws;
let currentPendingRequest = null;
let alertCountdownInterval = null;

const BANGALORE_CENTER = [12.9738, 77.6074]; // MG Road / Brigade Road Junction

// Web Audio API Chime generator
function playAlertChime() {
  try {
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(880, audioCtx.currentTime); // A5
    osc.frequency.exponentialRampToValueAtTime(1760, audioCtx.currentTime + 0.15); // A6
    gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.4);
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.start();
    osc.stop(audioCtx.currentTime + 0.4);
  } catch (e) {
    console.log("Audio alert blocked by browser autoplay policy");
  }
}

// 1. Initialize Map
function initMap() {
  map = L.map('map', {
    center: BANGALORE_CENTER,
    zoom: 16,
    zoomControl: false
  });

  L.control.zoom({ position: 'bottomright' }).addTo(map);

  // Modern Dark Map Tiles
  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap &copy; CARTO',
    subdomains: 'abcd',
    maxZoom: 19
  }).addTo(map);

  // Add Bangalore MG Road Junction Marker
  const junctionIcon = L.divIcon({
    className: 'custom-junction-icon',
    html: `
      <div style="background: #1e293b; border: 2px solid #38bdf8; border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 15px rgba(56, 189, 248, 0.6); color: #38bdf8; font-weight: bold; font-size: 11px;">
        🚦
      </div>`,
    iconSize: [32, 32],
    iconAnchor: [16, 16]
  });

  const jMarker = L.marker(BANGALORE_CENTER, { icon: junctionIcon }).addTo(map);
  jMarker.bindPopup("<b>Junction JN-04</b><br>MG Road - Brigade Road Corridor");
  junctionMarkers['JN-04'] = jMarker;

  // Draw Corridor Polylines
  const routes = [
    { id: 'SEG-N', name: 'North (Cubbon Rd)', coords: [[12.9820, 77.6074], [12.9738, 77.6074]], color: '#38bdf8' },
    { id: 'SEG-S', name: 'South (Brigade Rd)', coords: [[12.9650, 77.6074], [12.9738, 77.6074]], color: '#38bdf8' },
    { id: 'SEG-W', name: 'West (MG Rd West)', coords: [[12.9738, 77.5980], [12.9738, 77.6074]], color: '#818cf8' },
    { id: 'SEG-E', name: 'East (Trinity Circle)', coords: [[12.9738, 77.6165], [12.9738, 77.6074]], color: '#818cf8' }
  ];

  routes.forEach(r => {
    const pl = L.polyline(r.coords, {
      color: r.color,
      weight: 4,
      opacity: 0.6,
      dashArray: '6, 8'
    }).addTo(map);
    routePolylines[r.id] = pl;
  });

  setTimeout(() => {
    map.invalidateSize();
  }, 250);
}

// 2. WebSocket Communication
function connectWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = window.location.host || 'localhost:8000';
  const wsUrl = `${protocol}//${host}/ws`;

  ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    document.getElementById('ws-status-text').innerText = 'Connected (100% Real-Time)';
    document.getElementById('ws-status-dot').style.background = '#34d399';
    addLogEntry('WebSocket link established with AWS IoT Core / Backend', 'system');
  };

  ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    handleServerMessage(msg);
  };

  ws.onclose = () => {
    document.getElementById('ws-status-text').innerText = 'Reconnecting...';
    document.getElementById('ws-status-dot').style.background = '#ef4444';
    setTimeout(connectWebSocket, 2000);
  };
}

function handleServerMessage(msg) {
  if (msg.type === 'init_snapshot') {
    if (msg.thresholds && msg.thresholds.mode) {
      document.getElementById('sys-mode-badge').innerText = msg.thresholds.mode.toUpperCase();
    }
  } else if (msg.type === 'signal_state') {
    updateSignalDisplay(msg.data);
  } else if (msg.type === 'ambulance_update') {
    updateAmbulancePosition(msg.data);
  } else if (msg.type === 'priority_request') {
    handlePriorityRequest(msg.data, msg.action);
  } else if (msg.type === 'request_status') {
    handleRequestStatusUpdate(msg.data, msg.action);
  } else if (msg.type === 'alert') {
    addLogEntry(msg.message, 'alert');
  }
}

// 3. Update Signal Indicators
function updateSignalDisplay(data) {
  const state = data.state;
  const isPriority = data.is_priority;
  document.getElementById('signal-state-text').innerText = state;
  document.getElementById('signal-remaining-sec').innerText = `${data.remaining_s}s`;

  const nsRed = document.getElementById('ns-light-red');
  const nsYel = document.getElementById('ns-light-yellow');
  const nsGrn = document.getElementById('ns-light-green');

  const ewRed = document.getElementById('ew-light-red');
  const ewYel = document.getElementById('ew-light-yellow');
  const ewGrn = document.getElementById('ew-light-green');

  // Reset all
  [nsRed, nsYel, nsGrn, ewRed, ewYel, ewGrn].forEach(el => el && el.classList.remove('active'));

  if (state.startsWith('NS_GREEN') || state === 'PRIORITY_GREEN_NS') {
    nsGrn.classList.add('active');
    ewRed.classList.add('active');
  } else if (state === 'NS_YELLOW' || (state === 'PREEMPT_YELLOW' && data.active_group === 'NS')) {
    nsYel.classList.add('active');
    ewRed.classList.add('active');
  } else if (state.startsWith('EW_GREEN') || state === 'PRIORITY_GREEN_EW') {
    ewGrn.classList.add('active');
    nsRed.classList.add('active');
  } else if (state === 'EW_YELLOW' || (state === 'PREEMPT_YELLOW' && data.active_group === 'EW')) {
    ewYel.classList.add('active');
    nsRed.classList.add('active');
  } else if (state.includes('ALL_RED') || state.includes('PREEMPT_ALL_RED')) {
    nsRed.classList.add('active');
    ewRed.classList.add('active');
  } else if (state === 'FAULT_SAFE') {
    nsYel.classList.add('active');
    ewYel.classList.add('active');
  }

  // Priority indicator badge
  const pBadge = document.getElementById('priority-active-badge');
  if (isPriority) {
    pBadge.style.display = 'inline-block';
    pBadge.innerText = `🚨 PRIORITY ACTIVE: ${data.active_group || 'CORRIDOR'}`;
  } else {
    pBadge.style.display = 'none';
  }
}

// 4. Update Ambulance on Map
function updateAmbulancePosition(amb) {
  const id = amb.ambulance_id;
  const latLng = [amb.lat, amb.lon];

  if (!ambulanceMarkers[id]) {
    const ambIcon = L.divIcon({
      className: 'custom-amb-icon',
      html: `
        <div id="marker-${id}" style="background: #ef4444; border: 2px solid white; border-radius: 50%; width: 28px; height: 28px; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 20px rgba(239, 68, 68, 0.9); font-size: 14px; transform: rotate(${amb.heading_deg || 0}deg); transition: transform 0.3s ease;">
          🚑
        </div>`,
      iconSize: [28, 28],
      iconAnchor: [14, 14]
    });
    const marker = L.marker(latLng, { icon: ambIcon }).addTo(map);
    marker.bindPopup(`<b>Ambulance ${id}</b><br>Speed: ${amb.speed_kmh} km/h`);
    ambulanceMarkers[id] = marker;
  } else {
    ambulanceMarkers[id].setLatLng(latLng);
    const elem = document.getElementById(`marker-${id}`);
    if (elem) {
      elem.style.transform = `rotate(${amb.heading_deg || 0}deg)`;
    }
  }

  // Update Ambulance Sidebar Card
  renderAmbulanceCard(amb);
}

function renderAmbulanceCard(amb) {
  const container = document.getElementById('ambulance-list-container');
  let card = document.getElementById(`card-${amb.ambulance_id}`);

  const upcomingText = amb.upcoming ? `${amb.upcoming.junction_name} (${amb.upcoming.distance_m}m | ETA: ${amb.upcoming.eta_s}s)` : 'En route (Monitoring)';

  const cardHtml = `
    <div class="amb-header">
      <span class="amb-id">🚑 Ambulance ${amb.ambulance_id}</span>
      <span class="badge" style="background: rgba(239, 68, 68, 0.2); color: #f87171; padding: 2px 6px; border-radius: 4px; font-size: 0.75rem;">EMERGENCY</span>
    </div>
    <div class="amb-details">
      <div><b>Speed:</b> ${amb.speed_kmh} km/h</div>
      <div><b>Heading:</b> ${amb.heading_deg}°</div>
      <div style="grid-column: span 2; margin-top: 4px; color: #38bdf8;"><b>Next:</b> ${upcomingText}</div>
    </div>
  `;

  if (!card) {
    card = document.createElement('div');
    card.id = `card-${amb.ambulance_id}`;
    card.className = 'ambulance-card emergency';
    card.innerHTML = cardHtml;
    container.appendChild(card);
  } else {
    card.innerHTML = cardHtml;
  }
}

// 5. Handle Priority Request & Alert Banner
function handlePriorityRequest(req, action) {
  if (req.status === 'REQUESTED' && (req.priority_level === 'REQUEST' || req.priority_level === 'EMERGENCY')) {
    currentPendingRequest = req;
    showAlertBanner(req);
    playAlertChime();
    addLogEntry(`Priority requested for Ambulance ${req.ambulance_id} at ${req.junction_id} (ETA: ${req.eta_s}s)`, 'alert');
  } else if (req.status === 'COMPLETED') {
    hideAlertBanner();
    addLogEntry(`Ambulance ${req.ambulance_id} crossed ${req.junction_id}. Normal cycle restored.`, 'priority');
  }
}

function showAlertBanner(req) {
  const banner = document.getElementById('priority-alert-banner');
  document.getElementById('alert-amb-id').innerText = req.ambulance_id;
  document.getElementById('alert-junction-id').innerText = req.junction_id;
  document.getElementById('alert-distance').innerText = `${req.distance_m} m`;
  document.getElementById('alert-eta').innerText = `${req.eta_s} s`;
  document.getElementById('alert-approach').innerText = req.approach_id;
  banner.style.display = 'block';

  let countdown = 10;
  clearInterval(alertCountdownInterval);
  alertCountdownInterval = setInterval(() => {
    countdown--;
    document.getElementById('alert-timer-text').innerText = `${countdown}s`;
    if (countdown <= 0) {
      clearInterval(alertCountdownInterval);
    }
  }, 1000);
}

function hideAlertBanner() {
  document.getElementById('priority-alert-banner').style.display = 'none';
  clearInterval(alertCountdownInterval);
  currentPendingRequest = null;
}

function handleRequestStatusUpdate(req, action) {
  if (action === 'APPROVED') {
    hideAlertBanner();
    addLogEntry(`Police APPROVED green priority for ${req.ambulance_id} at ${req.junction_id}`, 'priority');
  } else if (action === 'REJECTED') {
    hideAlertBanner();
    addLogEntry(`Police REJECTED priority for ${req.ambulance_id}`, 'system');
  }
}

// 6. User Action Handlers (Approve / Reject / Override)
async function approveCurrentPriority() {
  if (!currentPendingRequest) return;
  const group = currentPendingRequest.approach_id.includes('-N') || currentPendingRequest.approach_id.includes('-S') ? 'NS' : 'EW';

  try {
    const res = await fetch(`/requests/${currentPendingRequest.request_id}/approve?group=${group}`, {
      method: 'POST',
      headers: { 'Authorization': 'Bearer token-police' }
    });
    if (res.ok) {
      hideAlertBanner();
    }
  } catch (e) {
    console.error("Approval error:", e);
  }
}

async function rejectCurrentPriority() {
  if (!currentPendingRequest) return;
  try {
    const res = await fetch(`/requests/${currentPendingRequest.request_id}/reject`, {
      method: 'POST',
      headers: { 'Authorization': 'Bearer token-police' }
    });
    if (res.ok) {
      hideAlertBanner();
    }
  } catch (e) {
    console.error("Reject error:", e);
  }
}

async function triggerManualOverride() {
  try {
    await fetch('/junctions/JN-04/resume-normal', {
      method: 'POST',
      headers: { 'Authorization': 'Bearer token-police' }
    });
    addLogEntry("Manual Override: Normal cycle restored on JN-04", "system");
  } catch (e) {
    console.error("Override error:", e);
  }
}

// 7. Simulation Trigger (North Route Run)
let simInterval = null;
function runDemoSimulation(route = 'north') {
  if (simInterval) clearInterval(simInterval);

  let coords;
  let approachBearing;
  if (route === 'north') {
    // Cubbon Road -> JN-04 (12.9820 -> 12.9738)
    coords = [
      [12.9820, 77.6074], [12.9805, 77.6074], [12.9790, 77.6074],
      [12.9775, 77.6074], [12.9760, 77.6074], [12.9748, 77.6074],
      [12.9740, 77.6074], [12.9738, 77.6074], [12.9725, 77.6074]
    ];
    approachBearing = 180.0;
  } else {
    // West Route
    coords = [
      [12.9738, 77.5980], [12.9738, 77.6000], [12.9738, 77.6025],
      [12.9738, 77.6045], [12.9738, 77.6060], [12.9738, 77.6074],
      [12.9738, 77.6090]
    ];
    approachBearing = 90.0;
  }

  let idx = 0;
  addLogEntry(`Started live simulation for Ambulance A102 along ${route.toUpperCase()} corridor...`, 'system');

  simInterval = setInterval(async () => {
    if (idx >= coords.length) {
      clearInterval(simInterval);
      addLogEntry("Simulation run completed.", "system");
      return;
    }

    const [lat, lon] = coords[idx];
    const payload = {
      ambulance_id: "A102",
      lat: lat,
      lon: lon,
      speed_kmh: 48.0,
      heading_deg: approachBearing,
      emergency: true,
      seq: idx + 1,
      source: "simulator"
    };

    try {
      await fetch('/telemetry', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    } catch (e) {
      console.error("Telemetry push failed:", e);
    }

    idx++;
  }, 1200);
}

// 8. Event Logger Helper
function addLogEntry(text, type = 'system') {
  const container = document.getElementById('event-log-container');
  if (!container) return;

  const entry = document.createElement('div');
  entry.className = `log-entry ${type}`;
  const timeStr = new Date().toLocaleTimeString();
  entry.innerHTML = `
    <div>${text}</div>
    <div class="log-time">${timeStr}</div>
  `;
  container.prepend(entry);
}

// Window load init
window.addEventListener('DOMContentLoaded', () => {
  initMap();
  connectWebSocket();
});
