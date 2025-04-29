import RPi.GPIO as GPIO
import time
import threading
import cv2
from ultralytics import YOLO
from time import sleep
import subprocess
from flask import Flask, request

from servo import move_servo, stop_servo
from lcd import display_message

# ---------------- Firebase ----------------
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials, firestore

cred = credentials.Certificate('firebase-key.json')  # <-- PUT YOUR JSON PATH
firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)

@app.route('/start-bottle-session', methods=['POST'])
def start_bottle_session():
    data = request.json
    mac = data.get('mac')
    ip = data.get('ip')

    if mac and ip:
        print(f"[✔] Session started with MAC: {mac}, IP: {ip}")
        return {'status': 'ok'}
    
    return {'status': 'error', 'message': 'Missing mac or ip'}, 400

# Start Flask in a background thread
def run_flask():
    app.run(host='0.0.0.0', port=80)

threading.Thread(target=run_flask, daemon=True).start()


# ---------------- Wi-Fi Time Management ----------------
from librouteros import connect

# MikroTik Settings
ROUTER_HOST = '192.168.50.1'
ROUTER_USERNAME = 'admin'
ROUTER_PASSWORD = ''
#TARGET_MAC = 'A2:DE:BF:8C:50:87'  # <<< Target device MAC address
#TARGET_MAC = None

# kung ang iyang queuePosition gikab sa db kay 1, ibutang ari ang TARGET_MAC

# Connect to MikroTik
try:
    api = connect(username=ROUTER_USERNAME, password=ROUTER_PASSWORD, host=ROUTER_HOST)
    print("[*] Connected to MikroTik Router.")
except Exception as e:
    print(f"[!] MikroTik connection failed: {e}")
    exit()

bindings = api.path('ip', 'hotspot', 'ip-binding')

# ------------------- Get TARGET_MAC from queuePosition == 1 -------------------
# start here
# dapat ma kuha niya ang queuePosition nga naay value 1 every time, 
# ang queuePosition mugawas sa db if naay nag click insert bottle
# ,kung walay queuePosition nga 1 kay wala ray mugawas,
# basta dapat makita if naay queuePosition = 1, 
# nya dapat if walay nay queuePosition kay di na makadawat ug WiFiTimeAvailable 
# ug TotalBottlesDeposited tong mac nga nakuha
TARGET_MAC = None
previous_user_id = None

def get_mac_with_queue_position_1():
    try:
        print("[*] Checking Firestore...")
        users_ref = db.collection('Users Collection')
        query = users_ref.where('queuePosition', '==', 1).limit(1)
        results = query.get()

        if results:
            user_doc = results[0]
            data = user_doc.to_dict()
            print(f"[Debug] Retrieved user data: {data}")

            user_id = data.get('UserID')
            if user_id:
                return user_id
            else:
                print("[!] User with queuePosition 1 has no UserID.")
        else:
            print("[!] No user found with queuePosition 1.")
    except Exception as e:
        print(f"[!] Firestore error: {e}")
    return None

# Function to update the TotalBottlesDeposited for the current device with queuePosition == 1
def update_total_bottles_for_current_user():
    try:
        print("[*] Updating TotalBottlesDeposited for the current active user with queuePosition == 1...")

        # Fetch the current active user (with queuePosition == 1)
        users_ref = db.collection('Users Collection')
        query = users_ref.where('queuePosition', '==', 1)
        results = query.get()

        if results:
            user_doc = results[0]
            data = user_doc.to_dict()
            user_id = data.get('UserID')

            # Check if the user ID has changed (this means a new device is now queuePosition == 1)
            global previous_user_id
            if user_id != previous_user_id:
                # Reset the bottles count for the old user if they no longer have queuePosition == 1
                if previous_user_id:
                    print(f"[✔] Stopping bottle count for the previous user {previous_user_id}")
                # Now, the previous user is this one, so we update their TotalBottlesDeposited
                previous_user_id = user_id

            # Increment the TotalBottlesDeposited for the current user
            current_bottles = data.get('TotalBottlesDeposited', 0)
            new_bottle_count = current_bottles + 1  # Increment by 1 for each detected bottle
            user_ref = users_ref.document(user_doc.id)
            user_ref.update({'TotalBottlesDeposited': new_bottle_count})

            print(f"[✔] TotalBottlesDeposited updated for user {user_id}. New count: {new_bottle_count}")

        else:
            print("[!] No active user with queuePosition == 1.")
    except Exception as e:
        print(f"[!] Error while updating TotalBottlesDeposited: {e}")

# Infinite loop that never exits unless you kill it
def monitor_firestore_for_queue():
    global TARGET_MAC
    while True:
        try:
            print("[*] Running Firestore queue check...", flush=True)
            mac = get_mac_with_queue_position_1()
            if mac:
                if mac != TARGET_MAC:
                    TARGET_MAC = mac
                    print(f"[✔] TARGET_MAC updated: {TARGET_MAC}", flush=True)

                    # Start updating the TotalBottlesDeposited for the current active user
                    update_total_bottles_for_current_user()
                else:
                    print(f"[*] TARGET_MAC remains the same: {TARGET_MAC}", flush=True)
            else:
                if TARGET_MAC is not None:
                    print("[*] No valid user found. Clearing TARGET_MAC.", flush=True)
                    TARGET_MAC = None

            time.sleep(1)
        except Exception as outer_err:
            print(f"[!] Firestore monitoring error: {outer_err}", flush=True)
            time.sleep(2)

# Start monitoring in a separate thread
threading.Thread(target=monitor_firestore_for_queue, daemon=True).start()
# kutob ari 
#-------------------------------------------------------------------------
def find_binding(mac_address):
    try:
        for entry in bindings('print'):
            if entry.get('mac-address', '').upper() == mac_address.upper():
                return entry
    except Exception as e:
        print(f"[!] Error fetching bindings: {e}")
    return None

def add_or_update_binding(mac_address, binding_type):
    try:
        existing = find_binding(mac_address)
        if existing:
            bindings.update(
                **{
                    '.id': existing['.id'],
                    'type': binding_type
                }
            )
            print(f"[*] Updated MAC {mac_address} to '{binding_type}'.")
        else:
            bindings.add(
                **{
                    'mac-address': mac_address,
                    'type': binding_type,
                    'comment': 'Connected'
                }
            )
            print(f"[*] Added new MAC {mac_address} with type '{binding_type}'.")
    except Exception as e:
        print(f"[!] Error adding/updating binding: {e}")

# --- Wi-Fi session variables ---
WiFiTimeAvailable = 0  # seconds
TotalBottlesDeposited = 0

# Function to update user based on MAC address
def update_user_by_mac(mac_address, bottles, wifi_time):
    try:
        users_ref = db.collection('Users Collection')
        query = users_ref.where('macAddress', '==', mac_address).limit(1)
        results = query.get()

        if results:
            user_doc = results[0]
            user_ref = users_ref.document(user_doc.id)
            user_ref.update({
                'TotalBottlesDeposited': bottles,
                'WiFiTimeAvailable': wifi_time
            })
            print(f"[+] Updated user {mac_address} - Bottles: {bottles}, WiFi Time: {wifi_time}")
        else:
            print(f"[!] No user found with MAC address {mac_address}")
    except Exception as e:
        print(f"[!] Failed to update user by MAC: {e}")

# Load your custom bottle-detection model
bottle_model = YOLO('detect/train11/weights/best.pt')

# Load pre-trained YOLOv8n model (general-purpose, COCO dataset)
general_model = YOLO('yolov8n.pt')

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

thread = threading.Thread(target=capture_frames, daemon=True)
thread.start()

display_message("Insert bottle")

last_detection_time = time.time()
last_servo_position = None
last_action = None

def set_servo_position(pos):
    global last_servo_position
    if last_servo_position != pos:
        move_servo(pos)
        last_servo_position = pos

# ---------------- Ultrasonic Sensor Logic ----------------

TRIG_PIN = 11
ECHO_PIN = 8
GPIO.setmode(GPIO.BOARD)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

container_full = False  # Shared flag

def get_distance():
    GPIO.output(TRIG_PIN, False)
    time.sleep(0.05)

    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_PIN, False)

    timeout = time.time() + 0.04
    while GPIO.input(ECHO_PIN) == 0:
        pulse_start = time.time()
        if time.time() > timeout:
            return None

    timeout = time.time() + 0.04
    while GPIO.input(ECHO_PIN) == 1:
        pulse_end = time.time()
        if time.time() > timeout:
            return None

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    return round(distance, 2)

# Monitoring container fullness and handling rejection
def monitor_container():
    global container_full
    try:
        while True:
            distance = get_distance()
            if distance is not None:
                print(f"[Ultrasonic] Distance: {distance} cm")
                if distance <= 4:  # Assuming distance < 4 cm indicates full
                    container_full = True
                    display_message("Container Full")
                    print("[Ultrasonic] Container Full - Rejecting Bottle")
                    set_servo_position(0)  # Reject bottle
                    sleep(1.5)
                    set_servo_position(0.5)  # Neutral position after rejection
                else:
                    container_full = False
            else:
                print("[Ultrasonic] Sensor error.")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Ultrasonic] Monitoring stopped.")
    finally:
        GPIO.cleanup()

# Start the container monitoring in a separate thread
threading.Thread(target=monitor_container, daemon=True).start()

try:
    while True:
        if frame is None:
            continue

        current_time = time.time()
        if current_time - last_detection_time >= 5:
            bottle_results = bottle_model(frame)[0]
            general_results = general_model(frame)[0]

            bottle_detected = False
            bottle_size = None  # 'small' or 'large'
            general_detected = False

            # Check bottle model
            if bottle_results.boxes is not None and len(bottle_results.boxes) > 0:
                frame_height, frame_width, _ = frame.shape  # Get frame size

            for box in bottle_results.boxes:
                confidence = box.conf[0].item()
                if confidence >= 0.7:
                    class_id = int(box.cls[0])
                    class_name = bottle_model.names[class_id].lower()

                    x1, y1, x2, y2 = box.xyxy[0]  # Get bounding box coordinates
                    box_width = x2 - x1
                    box_height = y2 - y1
                    box_area = box_width * box_height
                    frame_area = frame_width * frame_height
                    percentage = (box_area / frame_area) * 100

                    print(f"[{class_name}] Detected area: {percentage:.2f}% of frame")

                    if class_name == "small_bottle":
                        bottle_detected = True
                        bottle_size = 'small'
                        break
                    elif class_name == "large_bottle":
                        bottle_detected = True
                        bottle_size = 'large'
                        break

            # Check general model
            if general_results.boxes is not None and len(general_results.boxes) > 0:
                general_detected = True

            neutral_classes = ["bottle", "toilet", "surfboard", "bottles"]

            if bottle_detected and not container_full:
                display_message("Accepting Bottle")
                
                if bottle_size == 'small':
                    WiFiTimeAvailable += 5 * 60
                    #TotalBottlesDeposited += 1
                    print("[+] Small bottle detected: +5 mins Wi-Fi")
                elif bottle_size == 'large':
                    WiFiTimeAvailable += 10 * 60
                    #TotalBottlesDeposited += 1
                    print("[+] Large bottle detected: +10 mins Wi-Fi")

                update_user_by_mac(TARGET_MAC, TotalBottlesDeposited, WiFiTimeAvailable)

                set_servo_position(1)  # Accept
                sleep(1.5)
                set_servo_position(0.5)  # Neutral after accepting
                

            elif general_detected:
                go_neutral = False
                for box in general_results.boxes:
                    confidence = box.conf[0].item()
                    if confidence < 0.6:
                        continue  # Skip low-confidence detections

                    class_id = int(box.cls[0])
                    class_name = general_model.names[class_id].lower()

                    if class_name in neutral_classes:
                        go_neutral = True
                        break

                if go_neutral:
                    set_servo_position(0.5)
                    display_message("Insert bottle")
                else:
                    display_message("Rejected Bottle")
                    set_servo_position(0)  # Reject

            else:
                # No detection at all
                display_message("Insert bottle")
                set_servo_position(0.5)

            last_detection_time = current_time

except KeyboardInterrupt:
    print("🛑 Exiting gracefully...")

finally:
    cap.release()
    cv2.destroyAllWindows()
    set_servo_position(0.5)
    stop_servo()
