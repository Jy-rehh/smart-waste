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

# Connect to MikroTik Router
api = connect(username='admin', password='', host='192.168.50.1')

# Shared flag for container full status
container_full_event = threading.Event()

# Track already added MAC addresses
known_macs = set()

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

# Function to bypass the MAC address in MikroTik router
def bypass_internet(mac_address):
    try:
        # Find the binding entry for the MAC address
        bindings = api.path('ip', 'hotspot', 'ip-binding')
        binding = None

        for b in bindings:
            if b.get('mac-address', '').lower() == mac_address.lower():
                binding = b
                break

        if binding:
            # If the binding exists, update it
            print(f"[*] Found binding for {mac_address}, updating to bypass...")

            api.path('ip', 'hotspot', 'ip-binding').set(
                **{
                    '.id': binding['.id'],
                    'type': 'bypassed',  # This bypasses the MAC address, giving it internet access
                    'comment': 'Connected'
                }
            )

            print(f"[*] Successfully bypassed {mac_address}, user has internet!")
        else:
            # If no binding exists, add a new binding
            print(f"[!] No binding found for {mac_address}, adding new binding...")

            # Add a new binding for the MAC address
            api.path('ip', 'hotspot', 'ip-binding').add(
                **{
                    'mac-address': mac_address,
                    'type': 'bypassed',  # Set the binding type to bypassed
                    'comment': 'Connected'
                }
            )

            print(f"[*] Successfully added new binding for {mac_address}, user has internet!")

    except Exception as e:
        print(f"[!] Error during bypass: {e}")

# Function to revert to regular access when time runs out
def revert_to_regular(mac_address):
    try:
        # Find the binding entry for the MAC address
        bindings = api.path('ip', 'hotspot', 'ip-binding')
        binding = None

        for b in bindings:
            if b.get('mac-address', '').lower() == mac_address.lower():
                binding = b
                break

        if binding:
            print(f"[*] Found binding for {mac_address}, reverting to regular access...")

            # Revert the MAC address to regular access (remove bypass)
            api.path('ip', 'hotspot', 'ip-binding', set={
                '.id': binding['.id'],
                'type': 'regular'  # This reverts the MAC address to regular, without internet access
            })

            print(f"[*] Successfully reverted {mac_address} to regular access.")
        else:
            print(f"[!] No binding found for MAC: {mac_address}")

    except Exception as e:
        print(f"[!] Error during revert: {e}")

# Function to update user data in Firebase and add time based on bottle type
def update_user_data(mac_address, bottle_type):
    try:
        # Get the document for the user
        doc_ref = db.collection('Users Collection').document(mac_address)
        doc = doc_ref.get()

        if doc.exists:
            # User exists, update time and bottles deposited
            user_data = doc.to_dict()
            
            # Add time based on bottle type
            if bottle_type == "small_bottle":
                new_time = user_data['WiFiTimeAvailable'] + 5  # Add 5 minutes for small bottle
            elif bottle_type == "large_bottle":
                new_time = user_data['WiFiTimeAvailable'] + 10  # Add 10 minutes for large bottle
            else:
                new_time = user_data['WiFiTimeAvailable']  # No change if the bottle is not recognized

            new_bottles = user_data['TotalBottlesDeposited'] + 1  # Increment bottle count

            # Update Firestore document
            doc_ref.update({
                'WiFiTimeAvailable': new_time,
                'TotalBottlesDeposited': new_bottles
            })

            print(f"[*] Updated Firebase for {mac_address}. Time: {new_time}, Bottles: {new_bottles}")

        else:
            print(f"[!] No user found in Firebase for MAC: {mac_address}")

    except Exception as e:
        print(f"[!] Error while updating user data: {e}")

# Function to monitor and check if user's Wi-Fi time has expired
def check_time_expiry(mac_address):
    try:
        # Get the document for the user
        doc_ref = db.collection('Users Collection').document(mac_address)
        doc = doc_ref.get()

        if doc.exists:
            user_data = doc.to_dict()
            if user_data['WiFiTimeAvailable'] <= 0:
                print(f"[!] User {mac_address}'s WiFi time has expired, reverting access.")
                revert_to_regular(mac_address)
            else:
                print(f"[*] User {mac_address}'s WiFi time remaining: {user_data['WiFiTimeAvailable']} mins")

        else:
            print(f"[!] No user found in Firebase for MAC: {mac_address}")

    except Exception as e:
        print(f"[!] Error while checking time expiry: {e}")

# Function to handle bottle detection and bypass internet
def handle_bottle_detection(bottle_detected, mac_address, bottle_type):
    if bottle_detected:
        display_message("Accepting Bottle")
        set_servo_position(1)

        # Update Firebase based on bottle type (small or large)
        update_user_data(mac_address, bottle_type)

        # Bypass the internet for the user (grant them internet)
        bypass_internet(mac_address)

        # Pause for a short while before moving the servo back to neutral
        sleep(2)  # Wait for the bottle to be processed

        # Move the servo back to neutral (0.5) position after a short delay
        set_servo_position(0.5)  # Neutral position

        # Optionally, update the display to indicate the next action
        display_message("Insert bottle")
    else:
        display_message("Insert bottle")

# Main loop for bottle detection and checking expiration
try:
    while True:
        if frame is None:
            continue

        current_time = time.time()

        # Run both models every 5 seconds
        bottle_results = bottle_model(frame)[0]
        general_results = general_model(frame)[0]

        bottle_detected = False
        bottle_type = None

        # Bottle detection logic
        if bottle_results.boxes is not None and len(bottle_results.boxes) > 0:
            for box in bottle_results.boxes:
                confidence = box.conf[0].item()
                if confidence >= 0.7:
                    class_id = int(box.cls[0])
                    class_name = bottle_model.names[class_id].lower()
                    if class_name in ["small_bottle", "large_bottle"]:
                        bottle_detected = True
                        bottle_type = class_name  # Set the type of bottle detected
                        break

        # Handle bottle detection
        handle_bottle_detection(bottle_detected, "A2:DE:BF:8C:50:87", bottle_type)  # Replace with actual MAC address

        # Check if the user's time has expired
        check_time_expiry("A2:DE:BF:8C:50:87")  # Replace with actual MAC address

        sleep(1.5)

except KeyboardInterrupt:
    print("🛑 Exiting gracefully...")

finally:
    cap.release()
    cv2.destroyAllWindows()
    stop_servo()
