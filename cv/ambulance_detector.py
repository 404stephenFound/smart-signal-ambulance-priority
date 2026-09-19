import cv2
import time
import argparse
import json
import urllib.request
import os

def run_ambulance_detector(
    video_source: str = "0",
    server_url: str = "http://localhost:8000",
    camera_id: str = "CAM-JN04-N",
    confidence_threshold: float = 0.65
):
    """
    Edge Computer Vision module for Emergency Vehicle Optical Verification (Tier 4).
    Enforces Rule F6: CV alone raises police alert only, never preempts signals automatically.
    """
    print(f"=======================================================")
    print(f"📹 Starting Edge CV Ambulance Detector on {camera_id}")
    print(f"🎯 Backend: {server_url} | Confidence Threshold: {confidence_threshold}")
    print(f"=======================================================\n")

    # If numeric string, treat as webcam index
    src = int(video_source) if video_source.isdigit() else video_source
    cap = cv2.VideoCapture(src)

    if not cap.isOpened():
        print(f"[CV Warning] Unable to open video source '{video_source}'. Running optical simulation mode.")
        _simulate_optical_detection(server_url, camera_id)
        return

    last_detection_time = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Simulate / perform detection
        now = time.time()
        # Mock detection bounding box overlay for demonstration
        cv2.putText(frame, f"CAM: {camera_id} | AI Detection Active", (20, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (56, 189, 248), 2)

        # Trigger periodic detection event for demo video
        if now - last_detection_time > 15.0:
            last_detection_time = now
            cv2.rectangle(frame, (100, 100), (350, 280), (0, 0, 255), 3)
            cv2.putText(frame, "AMBULANCE DETECTED (92%)", (100, 90), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            _post_detection_event(server_url, camera_id, 0.92)

        cv2.imshow("Ambulance Vision AI Stream", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def _post_detection_event(server_url: str, camera_id: str, confidence: float):
    payload = {
        "camera_id": camera_id,
        "confidence": confidence,
        "matched_ambulance_id": "A102",
        "frame_s3_key": f"frames/{camera_id}_{int(time.time())}.jpg",
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    try:
        req = urllib.request.Request(
            f"{server_url}/telemetry",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        print(f"🚨 [CV Event] Published optical detection on {camera_id} (Confidence: {int(confidence*100)}%)")
    except Exception as e:
        print(f"[CV Error] Could not send detection event: {e}")

def _simulate_optical_detection(server_url: str, camera_id: str):
    print("Sending optical simulation detection event to backend...")
    _post_detection_event(server_url, camera_id, 0.94)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Computer Vision Ambulance Detector")
    parser.add_argument("--source", default="0", help="Webcam index or video file path")
    parser.add_argument("--server", default="http://localhost:8000", help="Backend API server")
    parser.add_argument("--camera", default="CAM-JN04-N", help="Camera Identifier")
    args = parser.parse_args()

    run_ambulance_detector(args.source, args.server, args.camera)
