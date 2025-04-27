import threading
import time
import cv2
from ultralytics import YOLO
from time import sleep
import subprocess
import RPi.GPIO as GPIO
from librouteros import connect
import firebase_admin
from firebase_admin import credentials, firestore

from servo import move_servo, stop_servo
from lcd import display_message
from container_full import monitor_container, container_full

# Initialize Firebase Admin with Firestore
cred = credentials.Certificate('firebase-key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Connect to MikroTik Router
api = connect(username='admin', password='', host='192.168.50.1')

# Function to get user info from MikroTik based on MAC address
def get_user_by_mac(mac_address):
    bindings = api.path('ip', 'hotspot', 'ip-binding')
    for b in bindings:
        if b.get('mac-address', '').lower() == mac_address.lower():
            return b  # Return binding info for the MAC address
    return None  # MAC not found

# Function to update Firebase user data
def update_user_data(mac_address, added_time=5):
    user_doc_ref = db.collection('Users Collection').document(mac_address)
    user_doc = user_doc_ref.get()

    if user_doc.exists:
        user_data = user_doc.to_dict()
        new_time = user_data.get('WiFiTimeAvailable', 0) + added_time
        new_bottle_count = user_data.get('TotalBottlesDeposited', 0) + 1

        # Update the user's time and bottle count in Firestore
        user_doc_ref.update({
            'WiFiTimeAvailable': new_time,
            'TotalBottlesDeposited': new_bottle_count
        })

        print(f"Updated user {mac_address}: +{added_time} minutes, Total Bottles: {new_bottle_count}")
    else:
        print(f"No user found for MAC address: {mac_address}")

# Load YOLO models
bottle_model = YOLO('detect/train11/weights/best.pt')
general_model = YOLO('yolov8n.pt')

# ESP32-CAM Stream
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

# Shared flag for container full status
container_full_event = threading.Event()

display_message("Insert bottle")

last_detection_time = time.time()
last_servo_position = None

def set_servo_position(pos):
    global last_servo_position
    if last_servo_position != pos:
        move_servo(pos)
        last_servo_position = pos

# Integrate with YOLO detection
def detect_and_update(frame):
    bottle_results = bottle_model(frame)[0]
    
    if bottle_results.boxes is not None and len(bottle_results.boxes) > 0:
        for box in bottle_results.boxes:
            confidence = box.conf[0].item()
            if confidence >= 0.7:
                class_id = int(box.cls[0])
                class_name = bottle_model.names[class_id].lower()
                if class_name in ["small_bottle", "large_bottle"]:
                    print("Bottle detected! Updating time...")
                    
                    # Example MAC address (replace with actual logic to get the MAC address)
                    mac_address = "A2:DE:BF:8C:50:87"  # Replace this with actual logic to get MAC address from MikroTik
                    update_user_data(mac_address)  # Add 5 minutes and increment bottle count
                    break

# Main loop for detection and updating user data
try:
    while True:
        if frame is None:
            continue

        # Check if container is full
        if container_full_event.is_set():
            display_message("Container Full")
            set_servo_position(0.5)  # Neutral
            sleep(1.5)
            continue

        current_time = time.time()
        if current_time - last_detection_time >= 5:
            detect_and_update(frame)  # Detect and update the user's data when a bottle is inserted
            sleep(1.5)
            set_servo_position(0.5)
            display_message("Insert bottle")
            last_detection_time = current_time

except KeyboardInterrupt:
    print("🛑 Exiting gracefully...")

finally:
    cap.release()
    cv2.destroyAllWindows()
    stop_servo()
