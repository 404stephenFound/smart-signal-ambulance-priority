import json
import os
import ssl
import threading
import time
from typing import Callable, Optional, Dict, Any

try:
    import paho.mqtt.client as mqtt
    PAHO_AVAILABLE = True
except ImportError:
    PAHO_AVAILABLE = False

class MQTTBridge:
    def __init__(
        self,
        endpoint: Optional[str] = None,
        port: int = 8883,
        ca_cert: Optional[str] = None,
        client_cert: Optional[str] = None,
        client_key: Optional[str] = None,
        client_id: str = "backend_service"
    ):
        self.endpoint = endpoint or os.environ.get("AWS_IOT_ENDPOINT")
        self.port = int(os.environ.get("AWS_IOT_PORT", port))
        self.ca_cert = ca_cert or os.environ.get("AWS_IOT_CA_PATH")
        self.client_cert = client_cert or os.environ.get("AWS_IOT_CERT_PATH")
        self.client_key = client_key or os.environ.get("AWS_IOT_KEY_PATH")
        self.client_id = client_id
        self.client = None
        self.is_connected = False
        self.message_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None

    def set_on_message(self, callback: Callable[[str, Dict[str, Any]], None]):
        self.message_callback = callback

    def start(self):
        if not PAHO_AVAILABLE:
            print("[MQTT] Paho-MQTT not installed. Running in local in-memory event bus mode.")
            return

        if not self.endpoint:
            print("[MQTT] No AWS_IOT_ENDPOINT configured. Running in internal event bus mode.")
            return

        try:
            self.client = mqtt.Client(client_id=self.client_id, protocol=mqtt.MQTTv311)
            
            # Configure TLS if certificates provided
            if self.ca_cert and os.path.exists(self.ca_cert):
                self.client.tls_set(
                    ca_certs=self.ca_cert,
                    certfile=self.client_cert,
                    keyfile=self.client_key,
                    cert_reqs=ssl.CERT_REQUIRED,
                    tls_version=ssl.PROTOCOL_TLSv1_2
                )

            self.client.on_connect = self._on_connect
            self.client.on_message = self._on_message
            self.client.connect_async(self.endpoint, self.port, 60)
            self.client.loop_start()
            print(f"[MQTT] Connecting to IoT Core endpoint {self.endpoint}:{self.port}...")
        except Exception as e:
            print(f"[MQTT] Connection initialization warning: {e}. Falling back to internal event bus.")

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.is_connected = True
            print("[MQTT] Successfully connected to AWS IoT Core MQTT broker.")
            # Subscribe to topics
            self.client.subscribe("ambulance/+/telemetry")
            self.client.subscribe("junction/+/state")
            self.client.subscribe("junction/+/heartbeat")
            self.client.subscribe("detections/+")
        else:
            print(f"[MQTT] Connect failed with code {rc}")

    def _on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            if self.message_callback:
                self.message_callback(msg.topic, payload)
        except Exception as e:
            print(f"[MQTT] Error parsing payload from topic {msg.topic}: {e}")

    def publish(self, topic: str, payload: Dict[str, Any]):
        if self.client and self.is_connected:
            try:
                self.client.publish(topic, json.dumps(payload), qos=1)
            except Exception as e:
                print(f"[MQTT] Publish error on topic {topic}: {e}")
        else:
            # When running without cloud broker, internal dispatch occurs directly in backend
            pass
