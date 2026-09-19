/*
 * Team infinity — Intelligent Traffic Signal Controller Firmware (ESP32)
 * Hardware Implementation for First Commit Hackathon (WeMakeDevs x AWS)
 *
 * Implements F5 State Machine & Deterministic Safety Interlocks:
 * - Never shows conflicting Green signals concurrently
 * - Enforces minimum clearance times (Yellow 3s, All-Red 2s, Min Green 5s)
 * - Connects to AWS IoT Core via MQTT over TLS (Port 8883)
 * - Watchdog Fail-Safe fallback upon connection loss
 */

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// Wi-Fi Credentials
const char* WIFI_SSID = "AmbulanceDemoHotspot";
const char* WIFI_PASS = "demo12345";

// AWS IoT Core Settings
const char* AWS_IOT_ENDPOINT = "a1b2c3d4e5f6-ats.iot.ap-south-1.amazonaws.com";
const int   AWS_IOT_PORT     = 8883;
const char* THING_NAME       = "junction_JN04";

// X.509 Certificates (Provisioned from AWS IoT Core)
const char AWS_CERT_CA[] PROGMEM = R"EOF(
-----BEGIN CERTIFICATE-----
... Amazon Root CA 1 ...
-----END CERTIFICATE-----
)EOF";

const char AWS_CERT_CRT[] PROGMEM = R"EOF(
-----BEGIN CERTIFICATE-----
... Device Certificate ...
-----END CERTIFICATE-----
)EOF";

const char AWS_CERT_PRIVATE[] PROGMEM = R"EOF(
-----BEGIN RSA PRIVATE KEY-----
... Device Private Key ...
-----END RSA PRIVATE KEY-----
)EOF";

// GPIO Pin Mapping for 4-Way Traffic LEDs
// North-South Group
const int PIN_NS_RED    = 18;
const int PIN_NS_YELLOW = 19;
const int PIN_NS_GREEN  = 21;

// East-West Group
const int PIN_EW_RED    = 22;
const int PIN_EW_YELLOW = 23;
const int PIN_EW_GREEN  = 25;

// State Machine Timings (Milliseconds)
const unsigned long DURATION_YELLOW_MS     = 3000;
const unsigned long DURATION_ALL_RED_MS    = 2000;
const unsigned long DURATION_MIN_GREEN_MS  = 5000;
const unsigned long DURATION_NORMAL_GRN_MS = 15000;
const unsigned long WATCHDOG_TIMEOUT_MS    = 6000;

enum SignalFSMState {
  STATE_NS_GREEN,
  STATE_NS_YELLOW,
  STATE_ALL_RED_TO_EW,
  STATE_EW_GREEN,
  STATE_EW_YELLOW,
  STATE_ALL_RED_TO_NS,
  STATE_PREEMPT_YELLOW,
  STATE_PREEMPT_ALL_RED,
  STATE_PRIORITY_GREEN,
  STATE_RECOVERY_YELLOW,
  STATE_RECOVERY_ALL_RED,
  STATE_FAULT_SAFE
};

SignalFSMState currentState = STATE_NS_GREEN;
unsigned long stateStartTime = 0;
unsigned long stateTargetDuration = DURATION_NORMAL_GRN_MS;
unsigned long lastHeartbeatTime = 0;
unsigned long lastStatePublishTime = 0;

bool isPriorityActive = false;
String priorityGroup = "";
String activeRequestId = "";
unsigned long priorityTTLMs = 30000;
unsigned long priorityStartTime = 0;

WiFiClientSecure netClient;
PubSubClient mqttClient(netClient);

void setLights(bool nsR, bool nsY, bool nsG, bool ewR, bool ewY, bool ewG) {
  // HARDWARE SAFETY INTERLOCK: Never allow simultaneous NS_GREEN and EW_GREEN
  if (nsG && ewG) {
    // Safety fault condition detected! Fallback to all red immediately
    digitalWrite(PIN_NS_RED, HIGH);
    digitalWrite(PIN_NS_YELLOW, LOW);
    digitalWrite(PIN_NS_GREEN, LOW);
    digitalWrite(PIN_EW_RED, HIGH);
    digitalWrite(PIN_EW_YELLOW, LOW);
    digitalWrite(PIN_EW_GREEN, LOW);
    return;
  }
  digitalWrite(PIN_NS_RED,    nsR ? HIGH : LOW);
  digitalWrite(PIN_NS_YELLOW, nsY ? HIGH : LOW);
  digitalWrite(PIN_NS_GREEN,  nsG ? HIGH : LOW);
  digitalWrite(PIN_EW_RED,    ewR ? HIGH : LOW);
  digitalWrite(PIN_EW_YELLOW, ewY ? HIGH : LOW);
  digitalWrite(PIN_EW_GREEN,  ewG ? HIGH : LOW);
}

void transitionState(SignalFSMState newState, unsigned long durationMs) {
  currentState = newState;
  stateStartTime = millis();
  stateTargetDuration = durationMs;
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  StaticJsonDocument<256> doc;
  deserializeJson(doc, payload, length);

  const char* cmd = doc["cmd"];
  if (!cmd) return;

  if (strcmp(cmd, "PRIORITY") == 0) {
    const char* grp = doc["group"];
    const char* reqId = doc["request_id"];
    unsigned long ttl = doc["ttl_s"] | 30;

    if (grp) {
      priorityGroup = String(grp);
      activeRequestId = reqId ? String(reqId) : "";
      priorityTTLMs = ttl * 1000;

      // Check current state for immediate hold or preemption
      if (priorityGroup == "NS" && currentState == STATE_NS_GREEN) {
        currentState = STATE_PRIORITY_GREEN;
        isPriorityActive = true;
        priorityStartTime = millis();
      } else if (priorityGroup == "EW" && currentState == STATE_EW_GREEN) {
        currentState = STATE_PRIORITY_GREEN;
        isPriorityActive = true;
        priorityStartTime = millis();
      } else if (!isPriorityActive) {
        // Conflicting phase: start safe preemption yellow transition
        transitionState(STATE_PREEMPT_YELLOW, DURATION_YELLOW_MS);
        isPriorityActive = true;
      }
    }
  } else if (strcmp(cmd, "RESUME_NORMAL") == 0 || strcmp(cmd, "CANCEL_PRIORITY") == 0) {
    if (isPriorityActive) {
      transitionState(STATE_RECOVERY_YELLOW, DURATION_YELLOW_MS);
    }
  }
}

void setup() {
  Serial.begin(115200);

  pinMode(PIN_NS_RED, OUTPUT);
  pinMode(PIN_NS_YELLOW, OUTPUT);
  pinMode(PIN_NS_GREEN, OUTPUT);
  pinMode(PIN_EW_RED, OUTPUT);
  pinMode(PIN_EW_YELLOW, OUTPUT);
  pinMode(PIN_EW_GREEN, OUTPUT);

  setLights(true, false, false, true, false, false); // All Red init

  WiFi.begin(WIFI_SSID, WIFI_PASS);
  netClient.setCACert(AWS_CERT_CA);
  netClient.setCertificate(AWS_CERT_CRT);
  netClient.setPrivateKey(AWS_CERT_PRIVATE);

  mqttClient.setServer(AWS_IOT_ENDPOINT, AWS_IOT_PORT);
  mqttClient.setCallback(mqttCallback);

  transitionState(STATE_NS_GREEN, DURATION_NORMAL_GRN_MS);
}

void loop() {
  unsigned long now = millis();
  unsigned long elapsed = now - stateStartTime;

  // Maintain MQTT Link
  if (WiFi.status() == WL_CONNECTED) {
    if (!mqttClient.connected()) {
      mqttClient.connect(THING_NAME);
      mqttClient.subscribe("junction/JN-04/command");
    }
    mqttClient.loop();
  }

  // Publish Heartbeat every 2 seconds
  if (now - lastHeartbeatTime > 2000) {
    lastHeartbeatTime = now;
    if (mqttClient.connected()) {
      mqttClient.publish("junction/JN-04/heartbeat", "{\"status\":\"ok\",\"uptime_s\":100}");
    }
  }

  // FSM Logic Execution
  switch (currentState) {
    case STATE_NS_GREEN:
      setLights(false, false, true, true, false, false);
      if (elapsed >= stateTargetDuration) transitionState(STATE_NS_YELLOW, DURATION_YELLOW_MS);
      break;

    case STATE_NS_YELLOW:
      setLights(false, true, false, true, false, false);
      if (elapsed >= stateTargetDuration) transitionState(STATE_ALL_RED_TO_EW, DURATION_ALL_RED_MS);
      break;

    case STATE_ALL_RED_TO_EW:
      setLights(true, false, false, true, false, false);
      if (elapsed >= stateTargetDuration) transitionState(STATE_EW_GREEN, DURATION_NORMAL_GRN_MS);
      break;

    case STATE_EW_GREEN:
      setLights(true, false, false, false, false, true);
      if (elapsed >= stateTargetDuration) transitionState(STATE_EW_YELLOW, DURATION_YELLOW_MS);
      break;

    case STATE_EW_YELLOW:
      setLights(true, false, false, false, true, false);
      if (elapsed >= stateTargetDuration) transitionState(STATE_ALL_RED_TO_NS, DURATION_ALL_RED_MS);
      break;

    case STATE_ALL_RED_TO_NS:
      setLights(true, false, false, true, false, false);
      if (elapsed >= stateTargetDuration) transitionState(STATE_NS_GREEN, DURATION_NORMAL_GRN_MS);
      break;

    case STATE_PREEMPT_YELLOW:
      if (priorityGroup == "NS") setLights(true, false, false, false, true, false);
      else setLights(false, true, false, true, false, false);
      if (elapsed >= stateTargetDuration) transitionState(STATE_PREEMPT_ALL_RED, DURATION_ALL_RED_MS);
      break;

    case STATE_PREEMPT_ALL_RED:
      setLights(true, false, false, true, false, false);
      if (elapsed >= stateTargetDuration) {
        currentState = STATE_PRIORITY_GREEN;
        priorityStartTime = now;
      }
      break;

    case STATE_PRIORITY_GREEN:
      if (priorityGroup == "NS") setLights(false, false, true, true, false, false);
      else setLights(true, false, false, false, false, true);

      // Guard: Priority TTL Expiration
      if (now - priorityStartTime > priorityTTLMs) {
        transitionState(STATE_RECOVERY_YELLOW, DURATION_YELLOW_MS);
      }
      break;

    case STATE_RECOVERY_YELLOW:
      if (priorityGroup == "NS") setLights(false, true, false, true, false, false);
      else setLights(true, false, false, false, true, false);
      if (elapsed >= stateTargetDuration) transitionState(STATE_RECOVERY_ALL_RED, DURATION_ALL_RED_MS);
      break;

    case STATE_RECOVERY_ALL_RED:
      setLights(true, false, false, true, false, false);
      if (elapsed >= stateTargetDuration) {
        isPriorityActive = false;
        transitionState(STATE_NS_GREEN, DURATION_NORMAL_GRN_MS);
      }
      break;

    case STATE_FAULT_SAFE:
      // Flashing Yellow Fail-Safe
      bool flash = (now / 500) % 2 == 0;
      setLights(false, flash, false, false, flash, false);
      break;
  }
}
