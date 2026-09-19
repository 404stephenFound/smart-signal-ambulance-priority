// Intelligent Traffic Priority & Police Control Dashboard Logic
// Claude-Inspired Minimalist Design — Team infinity

let map;
let junctionMarkers = {};
let ambulanceMarkers = {};
let routePolylines = {};
let radarCircle = null;
let ws;
let currentPendingRequest = null;
let alertCountdownInterval = null;
let currentRadiusM = 1500;
let currentRadarCenter = [12.9738, 77.6074]; // Default: MG Road Junction

const BANGALORE_CENTER = [12.9738, 77.6074]; // MG Road / Brigade Road Junction

// Network of Arterial Traffic Signals in the Corridor
const JUNCTION_REGISTRY = [
  { id: 'JN-04', name: 'MG Road - Brigade Road', lat: 12.9738, lon: 77.6074, primary: true },
  { id: 'JN-01', name: 'Trinity Circle', lat: 12.9738, lon: 77.6165, primary: false },
  { id: 'JN-02', name: 'Anil Kumble Circle', lat: 12.9738, lon: 77.5980, primary: false },
  { id: 'JN-03', name: 'Mayo Hall Junction', lat: 12.9738, lon: 77.6110, primary: false },
  { id: 'JN-05', name: 'Richmond Circle', lat: 12.9650, lon: 77.5980, primary: false },
  { id: 'JN-06', name: 'Cubbon Road - BRV', lat: 12.9820, lon: 77.6074, primary: false }
];

let activeAmbulancesData = {};

// Helper: Haversine distance in meters
function calcDistanceMeters(lat1, lon1, lat2, lon2) {
  const R = 6371000;
  const rad = Math.PI / 180;
  const dLat = (lat2 - lat1) * rad;
  const dLon = (lon2 - lon1) * rad;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * rad) * Math.cos(lat2 * rad) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return Math.round(R * c);
}

// Web Audio API Chime generator
function playAlertChime() {
  try {
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(880, audioCtx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(1760, audioCtx.currentTime + 0.15);
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

// 1. Initialize Map & Radar
function initMap() {
  map = L.map('map', {
    center: BANGALORE_CENTER,
    zoom: 15,
    zoomControl: false
  });

  L.control.zoom({ position: 'bottomright' }).addTo(map);

  // 100% Free OpenStreetMap Tiles (Dark midnight theme)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 19,
    className: 'dark-tiles'
  }).addTo(map);

  // Draw Radar Geofence Circle (Claude Minimalist Terracotta)
  radarCircle = L.circle(currentRadarCenter, {
    radius: currentRadiusM,
    color: '#cc785c',
    weight: 1.5,
    dashArray: '5, 7',
    fillColor: '#cc785c',
    fillOpacity: 0.05
  }).addTo(map);

  // Render all Traffic Signals in the Registry
  renderAllJunctionMarkers();

  // Draw Corridor Polylines
  const routes = [
    { id: 'SEG-N', name: 'North (Cubbon Rd)', coords: [[12.9820, 77.6074], [12.9738, 77.6074]], color: '#cc785c' },
    { id: 'SEG-S', name: 'South (Brigade Rd)', coords: [[12.9650, 77.6074], [12.9738, 77.6074]], color: '#cc785c' },
    { id: 'SEG-W', name: 'West (MG Rd West)', coords: [[12.9738, 77.5980], [12.9738, 77.6074]], color: '#a6a49c' },
    { id: 'SEG-E', name: 'East (Trinity Circle)', coords: [[12.9738, 77.6165], [12.9738, 77.6074]], color: '#a6a49c' }
  ];

  routes.forEach(r => {
    const pl = L.polyline(r.coords, {
      color: r.color,
      weight: 3,
      opacity: 0.5,
      dashArray: '4, 6'
    }).addTo(map);
    routePolylines[r.id] = pl;
  });

  setTimeout(() => {
    map.invalidateSize();
    applyRadiusFilter();
  }, 250);
}

// 2. Render and Manage Junction Markers
function renderAllJunctionMarkers() {
  JUNCTION_REGISTRY.forEach(j => {
    const isPrimary = j.id === 'JN-04';
    const borderColor = isPrimary ? '#cc785c' : '#525048';
    const junctionIcon = L.divIcon({
      className: 'custom-junction-marker',
      html: `
        <div id="junc-icon-${j.id}" class="junction-icon-housing" style="border-color: ${borderColor};">
          🚦
        </div>
        <div id="junc-tag-${j.id}" class="junction-label-tag">
          ${j.id}: ${j.name.split(' ')[0]}
        </div>`,
      iconSize: [44, 46],
      iconAnchor: [22, 23]
    });

    const marker = L.marker([j.lat, j.lon], { icon: junctionIcon }).addTo(map);
    marker.bindPopup(`
      <div style="font-family: 'Plus Jakarta Sans', sans-serif; padding: 4px 2px;">
        <div style="font-family: 'Newsreader', serif; color: #f4f3ee; font-size: 1.1rem; font-weight: 500;">${j.name} (${j.id})</div>
        <div style="font-size: 0.78rem; color: #a6a49c; margin-top: 2px;">Bangalore Arterial Traffic Signal</div>
        <div style="margin-top: 6px; font-size: 0.8rem; color: #d1cfc7;"><b>Control:</b> FSM Priority Engine</div>
        <div style="font-size: 0.75rem; color: #34d399; margin-top: 2px;">🟢 AWS IoT Core Link Synced</div>
      </div>
    `);
    junctionMarkers[j.id] = marker;
  });
}

// 3. Radar Radius Filter & Scanning
function setScanRadius(meters, elem) {
  currentRadiusM = meters;
  if (radarCircle) {
    radarCircle.setRadius(meters);
  }

  document.querySelectorAll('.radius-pill').forEach(b => b.classList.remove('active'));
  if (elem) elem.classList.add('active');

  applyRadiusFilter();
  addLogEntry(`Radar radius adjusted to ${meters >= 1000 ? (meters/1000)+'km' : meters+'m'}`, 'system');
}

function triggerRadarScan() {
  playAlertChime();
  if (radarCircle) {
    radarCircle.setStyle({ fillColor: '#34d399', fillOpacity: 0.18, color: '#34d399' });
    setTimeout(() => {
      radarCircle.setStyle({ fillColor: '#cc785c', fillOpacity: 0.05, color: '#cc785c' });
    }, 700);
  }
  applyRadiusFilter();
  const sigCount = document.getElementById('stat-signals-in-radius').innerText;
  const ambCount = document.getElementById('stat-amb-in-radius').innerText;
  addLogEntry(`Radar Sweep: ${sigCount} Traffic Lights & ${ambCount} Ambulances scanned in ${currentRadiusM}m zone`, 'priority');
}

function applyRadiusFilter() {
  let signalsInRadius = 0;
  let ambInRadius = 0;

  // Filter Junctions
  JUNCTION_REGISTRY.forEach(j => {
    const dist = calcDistanceMeters(currentRadarCenter[0], currentRadarCenter[1], j.lat, j.lon);
    const inRange = dist <= currentRadiusM;
    const iconElem = document.getElementById(`junc-icon-${j.id}`);
    const tagElem = document.getElementById(`junc-tag-${j.id}`);

    if (inRange) {
      signalsInRadius++;
      if (iconElem) iconElem.classList.remove('dimmed');
      if (tagElem) tagElem.style.opacity = '1';
    } else {
      if (iconElem) iconElem.classList.add('dimmed');
      if (tagElem) tagElem.style.opacity = '0.3';
    }
  });

  // Filter Ambulances
  Object.values(activeAmbulancesData).forEach(amb => {
    const dist = calcDistanceMeters(currentRadarCenter[0], currentRadarCenter[1], amb.lat, amb.lon);
    if (dist <= currentRadiusM) {
      ambInRadius++;
    }
  });

  const sigElem = document.getElementById('stat-signals-in-radius');
  if (sigElem) sigElem.innerText = signalsInRadius;
  const ambElem = document.getElementById('stat-amb-in-radius');
  if (ambElem) ambElem.innerText = ambInRadius;
}

// 4. WebSocket Communication
function connectWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = window.location.host || 'localhost:8000';
  const wsUrl = `${protocol}//${host}/ws`;

  ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    const statusText = document.getElementById('ws-status-text');
    if (statusText) statusText.innerText = 'Connected (100% Real-Time)';
    const dot = document.getElementById('ws-status-dot');
    if (dot) dot.style.background = '#34d399';
    addLogEntry('WebSocket link established with AWS IoT Core / Backend', 'system');
  };

  ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    handleServerMessage(msg);
  };

  ws.onclose = () => {
    const statusText = document.getElementById('ws-status-text');
    if (statusText) statusText.innerText = 'Reconnecting...';
    const dot = document.getElementById('ws-status-dot');
    if (dot) dot.style.background = '#ef4444';
    setTimeout(connectWebSocket, 2000);
  };
}

function handleServerMessage(msg) {
  if (msg.type === 'init_snapshot') {
    if (msg.thresholds && msg.thresholds.mode) {
      const modeBadge = document.getElementById('sys-mode-badge');
      if (modeBadge) modeBadge.innerText = msg.thresholds.mode.toUpperCase();
    }
    if (msg.ambulances) {
      msg.ambulances.forEach(a => updateAmbulancePosition(a));
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

// 5. Update Signal Indicators
function updateSignalDisplay(data) {
  const state = data.state;
  const isPriority = data.is_priority;
  const stateElem = document.getElementById('signal-state-text');
  if (stateElem) stateElem.innerText = state;
  const secElem = document.getElementById('signal-remaining-sec');
  if (secElem) secElem.innerText = `${data.remaining_s}s`;

  const nsRed = document.getElementById('ns-light-red');
  const nsYel = document.getElementById('ns-light-yellow');
  const nsGrn = document.getElementById('ns-light-green');

  const ewRed = document.getElementById('ew-light-red');
  const ewYel = document.getElementById('ew-light-yellow');
  const ewGrn = document.getElementById('ew-light-green');

  // Reset all
  [nsRed, nsYel, nsGrn, ewRed, ewYel, ewGrn].forEach(el => el && el.classList.remove('active'));

  if (state.startsWith('NS_GREEN') || state === 'PRIORITY_GREEN_NS') {
    if (nsGrn) nsGrn.classList.add('active');
    if (ewRed) ewRed.classList.add('active');
  } else if (state === 'NS_YELLOW' || (state === 'PREEMPT_YELLOW' && data.active_group === 'NS')) {
    if (nsYel) nsYel.classList.add('active');
    if (ewRed) ewRed.classList.add('active');
  } else if (state.startsWith('EW_GREEN') || state === 'PRIORITY_GREEN_EW') {
    if (ewGrn) ewGrn.classList.add('active');
    if (nsRed) nsRed.classList.add('active');
  } else if (state === 'EW_YELLOW' || (state === 'PREEMPT_YELLOW' && data.active_group === 'EW')) {
    if (ewYel) ewYel.classList.add('active');
    if (nsRed) nsRed.classList.add('active');
  } else if (state.includes('ALL_RED') || state.includes('PREEMPT_ALL_RED')) {
    if (nsRed) nsRed.classList.add('active');
    if (ewRed) ewRed.classList.add('active');
  } else if (state === 'FAULT_SAFE') {
    if (nsYel) nsYel.classList.add('active');
    if (ewYel) ewYel.classList.add('active');
  }

  // Priority indicator badge
  const pBadge = document.getElementById('priority-active-badge');
  if (pBadge) {
    if (isPriority) {
      pBadge.style.display = 'inline-block';
      pBadge.innerText = `PRIORITY: ${data.active_group || 'CORRIDOR'}`;
    } else {
      pBadge.style.display = 'none';
    }
  }
}

// 6. Update Ambulance on Map & Scanner List
function updateAmbulancePosition(amb) {
  const id = amb.ambulance_id;
  const latLng = [amb.lat, amb.lon];
  activeAmbulancesData[id] = amb;

  if (!ambulanceMarkers[id]) {
    const ambIcon = L.divIcon({
      className: 'custom-amb-icon',
      html: `
        <div id="marker-${id}" style="background: #cc785c; border: 1.5px solid #ffffff; border-radius: 50%; width: 26px; height: 26px; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.5); font-size: 13px; transform: rotate(${amb.heading_deg || 0}deg); transition: transform 0.3s ease;">
          🚑
        </div>`,
      iconSize: [26, 26],
      iconAnchor: [13, 13]
    });
    const marker = L.marker(latLng, { icon: ambIcon }).addTo(map);
    marker.bindPopup(`<div style="font-family: 'Plus Jakarta Sans', sans-serif;"><b style="font-family: 'Newsreader', serif; font-size: 1rem;">Ambulance ${id}</b><br><span style="color: #a6a49c; font-size: 0.8rem;">Speed: ${amb.speed_kmh} km/h • Heading: ${amb.heading_deg}°</span></div>`);
    ambulanceMarkers[id] = marker;
  } else {
    ambulanceMarkers[id].setLatLng(latLng);
    const elem = document.getElementById(`marker-${id}`);
    if (elem) {
      elem.style.transform = `rotate(${amb.heading_deg || 0}deg)`;
    }
  }

  renderAmbulanceCard(amb);
  applyRadiusFilter();
}

function renderAmbulanceCard(amb) {
  const container = document.getElementById('ambulance-list-container');
  if (!container) return;
  let card = document.getElementById(`card-${amb.ambulance_id}`);

  const upcomingText = amb.upcoming ? `${amb.upcoming.junction_name} (${amb.upcoming.distance_m}m | ETA: ${amb.upcoming.eta_s}s)` : 'En route (Monitoring)';

  const cardHtml = `
    <div class="amb-header" onclick="focusAmbulance('${amb.ambulance_id}')" style="cursor: pointer;">
      <span class="amb-id">🚑 Ambulance ${amb.ambulance_id}</span>
      <span class="badge" style="background: rgba(204, 120, 92, 0.15); color: #e08a68; border: 1px solid rgba(204, 120, 92, 0.3); padding: 2px 6px; border-radius: 4px; font-size: 0.72rem; font-family: var(--font-mono); font-weight: 600;">EMERGENCY</span>
    </div>
    <div class="amb-details">
      <div><b>Speed:</b> ${amb.speed_kmh} km/h</div>
      <div><b>Heading:</b> ${amb.heading_deg}°</div>
      <div style="grid-column: span 2; margin-top: 4px; color: #cc785c;"><b>Next:</b> ${upcomingText}</div>
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

function focusAmbulance(id) {
  const amb = activeAmbulancesData[id];
  if (amb && map) {
    map.flyTo([amb.lat, amb.lon], 16, { duration: 1 });
  }
}

// 7. Handle Priority Request & Alert Banner
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
  if (!banner) return;
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
    const timerElem = document.getElementById('alert-timer-text');
    if (timerElem) timerElem.innerText = `${countdown}s`;
    if (countdown <= 0) {
      clearInterval(alertCountdownInterval);
    }
  }, 1000);
}

function hideAlertBanner() {
  const banner = document.getElementById('priority-alert-banner');
  if (banner) banner.style.display = 'none';
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

// 8. User Action Handlers (Approve / Reject / Override)
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

// 9. Single & Multi-Fleet Simulation Handlers
let simInterval = null;
let fleetInterval = null;

function runDemoSimulation(route = 'north') {
  if (simInterval) clearInterval(simInterval);
  if (fleetInterval) clearInterval(fleetInterval);

  let coords;
  let approachBearing;
  const ambId = route === 'north' ? "A102" : "A105";

  if (route === 'north') {
    coords = [
      [12.9820, 77.6074], [12.9805, 77.6074], [12.9790, 77.6074],
      [12.9775, 77.6074], [12.9760, 77.6074], [12.9748, 77.6074],
      [12.9740, 77.6074], [12.9738, 77.6074], [12.9725, 77.6074]
    ];
    approachBearing = 180.0;
  } else {
    coords = [
      [12.9738, 77.5980], [12.9738, 77.6000], [12.9738, 77.6025],
      [12.9738, 77.6045], [12.9738, 77.6060], [12.9738, 77.6074],
      [12.9738, 77.6090]
    ];
    approachBearing = 90.0;
  }

  let idx = 0;
  addLogEntry(`Started live simulation for Ambulance ${ambId} along ${route.toUpperCase()} corridor...`, 'system');

  simInterval = setInterval(async () => {
    if (idx >= coords.length) {
      clearInterval(simInterval);
      addLogEntry(`Simulation run for ${ambId} completed.`, "system");
      return;
    }

    const [lat, lon] = coords[idx];
    const payload = {
      ambulance_id: ambId,
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

// Multi-Fleet Simultaneous Conflict Simulation
function runMultiFleetSimulation() {
  if (simInterval) clearInterval(simInterval);
  if (fleetInterval) clearInterval(fleetInterval);

  const fleet = [
    {
      id: "A102",
      name: "North Route (Cubbon)",
      heading: 180.0,
      coords: [
        [12.9820, 77.6074], [12.9800, 77.6074], [12.9780, 77.6074],
        [12.9760, 77.6074], [12.9745, 77.6074], [12.9738, 77.6074], [12.9720, 77.6074]
      ]
    },
    {
      id: "A101",
      name: "East Route (Trinity)",
      heading: 270.0,
      coords: [
        [12.9738, 77.6165], [12.9738, 77.6140], [12.9738, 77.6110],
        [12.9738, 77.6090], [12.9738, 77.6074], [12.9738, 77.6050]
      ]
    },
    {
      id: "A103",
      name: "South Route (Brigade)",
      heading: 0.0,
      coords: [
        [12.9650, 77.6074], [12.9675, 77.6074], [12.9700, 77.6074],
        [12.9720, 77.6074], [12.9738, 77.6074], [12.9755, 77.6074]
      ]
    }
  ];

  let step = 0;
  const maxSteps = 8;
  addLogEntry("🚑 Starting Multi-Ambulance Fleet Radar Conflict Simulation (A101, A102, A103)...", "alert");
  playAlertChime();

  fleetInterval = setInterval(async () => {
    if (step >= maxSteps) {
      clearInterval(fleetInterval);
      addLogEntry("Multi-Ambulance fleet conflict simulation finished.", "system");
      return;
    }

    for (const amb of fleet) {
      const pt = amb.coords[Math.min(step, amb.coords.length - 1)];
      const payload = {
        ambulance_id: amb.id,
        lat: pt[0],
        lon: pt[1],
        speed_kmh: 46.0,
        heading_deg: amb.heading,
        emergency: true,
        seq: step + 1,
        source: "fleet_sim"
      };

      try {
        await fetch('/telemetry', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
      } catch (e) {
        console.error("Fleet telemetry push error:", e);
      }
    }

    step++;
  }, 1200);
}

// 10. Event Logger Helper
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
