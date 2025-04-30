import threading
import time
import cv2
from ultralytics import YOLO
from time import sleep
import subprocess
import RPi.GPIO as GPIO
from librouteros import connect
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from servo import move_servo, stop_servo
from lcd import display_message
from container_full import monitor_container, container_full

# Load YOLO models
bottle_model = YOLO('detect/train11/weights/best.pt')
general_model = YOLO('yolov8n.pt')

# Initialize Firebase Admin with Firestore
cred = credentials.Certificate('firebase-key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

container_full_event = threading.Event()

esp32_cam_url = "http://192.168.8.100:81/stream"
cap = cv2.VideoCapture(esp32_cam_url)

if not cap.isOpened():
    print("❌ Failed to connect to ESP32-CAM. Check IP or Wi-Fi.")
    exit()

frame = None

# Thread to capture video frames
def capture_frames():
    global frame
    while True:
        ret, new_frame = cap.read()
        if ret:
            frame = new_frame

# Start video capture thread
frame_thread = threading.Thread(target=capture_frames, daemon=True)
frame_thread.start()

# Start ultrasonic container monitor thread
ultrasonic_thread = threading.Thread(target=monitor_container, daemon=True)
ultrasonic_thread.start()

# Function to set servo position
def set_servo_position(pos):
    move_servo(pos)

# Monitor container full status in main loop
try:
    while True:
        if frame is None:
            continue

        # Check if container is full
        if container_full_event.is_set():  # Check if container_full_event is set
            display_message("Container Full")
            set_servo_position(0.5)  # Neutral
            sleep(1.5)
            continue

        current_time = time.time()

        # Run both models every 5 seconds
        bottle_results = bottle_model(frame)[0]
        general_results = general_model(frame)[0]

        # Flags for detection
        bottle_detected = False
        general_detected = False

        # General detection
        if general_results.boxes is not None and len(general_results.boxes) > 0:
            general_detected = True

        # Bottle detection
        if bottle_results.boxes is not None and len(bottle_results.boxes) > 0:
            for box in bottle_results.boxes:
                confidence = box.conf[0].item()
                if confidence >= 0.7:
                    class_id = int(box.cls[0])
                    class_name = bottle_model.names[class_id].lower()
                    if class_name in ["small_bottle", "large_bottle"]:
                        bottle_detected = True
                        break

        # Decision logic for bottle detection
        neutral_classes = ["bottle", "toilet", "surfboard"]

        if bottle_detected:
            display_message("Accepting Bottle")
            set_servo_position(1)
            sleep(2)
            set_servo_position(0.5)  # Neutral position
            display_message("Insert bottle")
            continue  # Exit after handling the detected bottle

        elif general_detected:
            go_neutral = False
            for box in general_results.boxes:
                confidence = box.conf[0].item()
                if confidence < 0.6:
                    continue

                class_id = int(box.cls[0])
                class_name = general_model.names[class_id].lower()
                print(f"Detected class from general model: {class_name} with confidence: {confidence}")

                if class_name in neutral_classes:
                    go_neutral = True
                    break

            if go_neutral:
                set_servo_position(0.5)
                display_message("Insert bottle")
            else:
                display_message("Object Rejected")
                set_servo_position(0)

        else:
            set_servo_position(0.5)
            display_message("Insert bottle")
            continue

        sleep(1.5)
        set_servo_position(0.5)
        display_message("Insert bottle")

except KeyboardInterrupt:
    print("🛑 Exiting gracefully...")

finally:
    cap.release()
    cv2.destroyAllWindows()
    stop_servo()
