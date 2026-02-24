import cv2
import pandas as pd
import os
import json
from ultralytics import YOLO
from datetime import timedelta
import time

# ==============================
# CONFIG
# ==============================

VIDEO_SOURCE = "theft.mp4"   # or use 0 for webcam
POS_LOG_FILE = "pos_logs.csv"
ALERT_FILE = "alerts.txt"
REAL_TIME_DATA_FILE = "realtime_data.json"
IMAGE_FOLDER = "theft_images"

CONFIDENCE = 0.4

# ==============================
# SETUP
# ==============================

os.makedirs(IMAGE_FOLDER, exist_ok=True)
open(ALERT_FILE, "w").close()

# Initialize real-time data file
initial_data = {
    "status": "running",
    "current_frame": None,
    "current_time": "0:00:00",
    "alerts": [],
    "people_count": 0,
    "objects_detected": []
}
with open(REAL_TIME_DATA_FILE, "w") as f:
    json.dump(initial_data, f)

# Load POS logs
pos_transactions = []
if os.path.exists(POS_LOG_FILE):
    pos_data = pd.read_csv(POS_LOG_FILE)
    pos_times = set(pos_data["timestamp"].astype(str))
    pos_transactions = pos_data.to_dict('records')
else:
    pos_times = set()
    pos_transactions = []

# Load YOLO model
model = YOLO("yolov8n.pt")

# Open video
cap = cv2.VideoCapture(VIDEO_SOURCE)

if not cap.isOpened():
    print("ERROR: Cannot open video")
    exit()

# Get REAL FPS from video
fps = cap.get(cv2.CAP_PROP_FPS)

if fps == 0:
    fps = 60
frame_delay = int(1000 / fps)

frame_count = 0
last_alert_time = ""

print("System Started...")
print("Real-time detection running...")

# ==============================
# FUNCTIONS
# ==============================

def seconds_to_timestamp(seconds):
    return str(timedelta(seconds=int(seconds)))

def save_alert(timestamp, frame):

    text = f"THEFT DETECTED at {timestamp}"

    print(text)

    with open(ALERT_FILE, "a") as f:
        f.write(text + "\n")

    filename = f"{IMAGE_FOLDER}/theft_{timestamp.replace(':','-')}.jpg"
    cv2.imwrite(filename, frame)
    
    # Update real-time data
    try:
        with open(REAL_TIME_DATA_FILE, "r") as f:
            data = json.load(f)
    except:
        data = {"alerts": []}
    
    if "alerts" not in data:
        data["alerts"] = []
    
    data["alerts"].append({
        "timestamp": timestamp,
        "image": filename,
        "message": text
    })
    
    with open(REAL_TIME_DATA_FILE, "w") as f:
        json.dump(data, f)

def update_realtime_data(current_time, frame, people_count, objects_detected, theft_detected):
    """Update real-time data for streaming to app.py"""
    try:
        with open(REAL_TIME_DATA_FILE, "r") as f:
            data = json.load(f)
    except:
        data = {}
    
    # Get POS transactions for display
    pos_for_display = []
    if current_time in pos_times:
        matching = [t for t in pos_transactions if str(t['timestamp']) == current_time]
        pos_for_display = matching
    
    data.update({
        "status": "running",
        "current_time": current_time,
        "people_count": people_count,
        "objects_detected": objects_detected,
        "theft_detected": theft_detected,
        "current_pos_transaction": pos_for_display,
        "all_pos_transactions": pos_transactions,
        "timestamp": time.time()
    })
    
    with open(REAL_TIME_DATA_FILE, "w") as f:
        json.dump(data, f)

# ==============================
# MAIN LOOP (REAL TIME)
# ==============================

while True:

    start_time = time.time()

    ret, frame = cap.read()

    if not ret:
        break

    frame_count += 1

    seconds = frame_count / fps
    current_time = seconds_to_timestamp(seconds)

    # YOLO detection
    results = model(frame, conf=CONFIDENCE, verbose=False)

    person_detected = False
    drawer_detected = False

    for box in results[0].boxes:

        class_id = int(box.cls)
        class_name = model.names[class_id]

        x1, y1, x2, y2 = map(int, box.xyxy[0])

        if class_name == "person":

            person_detected = True

            cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)
            cv2.putText(frame,"Person",(x1,y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,255,0),2)

        if class_name in ["cell phone","laptop","keyboard"]:

            drawer_detected = True

            cv2.rectangle(frame,(x1,y1),(x2,y2),(255,0,0),2)
            cv2.putText(frame,"Drawer",(x1,y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,0,0),2)

    theft = False

    if drawer_detected and current_time not in pos_times:
        theft = True

    if drawer_detected and not person_detected:
        theft = True

    if theft and current_time != last_alert_time:

        save_alert(current_time, frame)

        last_alert_time = current_time

        cv2.putText(frame,
                    "THEFT ALERT",
                    (50,50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0,0,255),
                    3)

    # Count detections
    people_count = sum(1 for box in results[0].boxes if model.names[int(box.cls)] == "person")
    objects = [model.names[int(box.cls)] for box in results[0].boxes if model.names[int(box.cls)] in ["cell phone", "laptop", "keyboard"]]
    
    cv2.putText(frame,
                "SecurePOS AI - Real Time",
                (10,30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255,255,255),
                2)
    
    cv2.putText(frame,
                f"People: {people_count} | Objects: {len(objects)}",
                (10,70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255,255,255),
                2)

    # Update real-time data
    update_realtime_data(current_time, frame, people_count, objects, theft)

    cv2.imshow("SecurePOS AI", frame)

    # REAL-TIME DELAY CONTROL
    elapsed = (time.time() - start_time) * 1000
    wait_time = max(1, int(frame_delay - elapsed))

    if cv2.waitKey(wait_time) == 27:
        break

cap.release()
cv2.destroyAllWindows()

# Mark as stopped
with open(REAL_TIME_DATA_FILE, "w") as f:
    json.dump({"status": "stopped"}, f)

print("System Stopped")
