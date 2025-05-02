import RPi.GPIO as GPIO
import time
import threading
import cv2
from ultralytics import YOLO
from time import sleep
import subprocess
from flask import Flask, request
from firebase_admin import firestore, db as realtime_db
#from servo import move_servo, stop_servo
from verify import setup_ultrasonic, get_distance
from servo import setup_servo, move_servo, stop_servo
from lcd import display_message


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

setup_ultrasonic()
setup_servo()

# ---------------- Firebase ----------------
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials, firestore

cred = credentials.Certificate('firebase-key.json')  # <-- PUT YOUR JSON PATH
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://smart-waste-c39ac-default-rtdb.firebaseio.com/'
})
db = firestore.client()

app = Flask(__name__)

@app.route('/start-bottle-session', methods=['POST'])
def start_bottle_session():
    data = request.json
    mac = data.get('mac')
    ip = data.get('ip')

    if mac and ip:
        #print(f"[✔] Session started with MAC: {mac}, IP: {ip}")
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
TARGET_MAC = None
previous_user_id = None

def get_mac_with_queue_position_1():
    try:
        #("[*] Checking Firestore...")
        users_ref = db.collection('Users Collection')
        query = users_ref.where('queuePosition', '==', 1).limit(1)
        results = query.get()

        if results:
            user_doc = results[0]
            data = user_doc.to_dict()
            #print(f"[Debug] Retrieved user data: {data}")

            user_id = data.get('UserID')
            if user_id:
                return user_id
            #else:
                #print("[!] User with queuePosition 1 has no UserID.")
        #else:
            #print("[!] No user found with queuePosition 1.")
    except Exception as e:
        print(f"[!] Firestore error: {e}")
    return None
def sync_firestore_to_realtime():
    try:
        firestore_users = db.collection('Users Collection').where('queuePosition', '==', 1).stream()

        for user_doc in firestore_users:
            user_data = user_doc.to_dict()
            mac_address = user_data.get('UserID')
            if not mac_address:
                continue

            mac_sanitized = mac_address.replace(":", "-")
            rt_ref = realtime_db.reference(f'users/{mac_sanitized}')
            rt_user = rt_ref.get()

            if rt_user and rt_user.get('UserID') == mac_address:
                # Get the current value from Realtime DB
                current_wifi_time = rt_user.get('WiFiTimeAvailable', 0)

                # Get the WiFi time increment based on the bottle size (5 minutes for small, 10 for large)
                wifi_time_increment = 5 * 60  # Default to 5 minutes (in seconds)

                if user_data.get('bottle_size') == 'large':
                    wifi_time_increment = 10 * 60  # 10 minutes for large bottle

                # Update only if the new WiFi time is different
                new_wifi_time = current_wifi_time + wifi_time_increment
                rt_ref.update({
                    'WiFiTimeAvailable': new_wifi_time,
                    'TotalBottlesDeposited': user_data.get('TotalBottlesDeposited', 0)
                })
                print(f"[✓] Synced user {mac_address} to Realtime DB. New WiFiTimeAvailable: {new_wifi_time}")
            else:
                print(f"[!] Realtime DB entry for {mac_address} not found or mismatched.")
    except Exception as e:
        print(f"[!] Sync failed: {e}")

        
# Function to update the TotalBottlesDeposited for the current device with queuePosition == 1
def update_total_bottles_for_current_user():
    try:
        #print("[*] Updating TotalBottlesDeposited for the current active user with queuePosition == 1...")

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

        #else:
            #print("[!] No active user with queuePosition == 1.")
    except Exception as e:
        print(f"[!] Error while updating TotalBottlesDeposited: {e}")

# Infinite loop that never exits unless you kill it
def monitor_firestore_for_queue():
    global TARGET_MAC
    while True:
        try:
            #print("[*] Running Firestore queue check...", flush=True)
            mac = get_mac_with_queue_position_1()
            if mac:
                if mac != TARGET_MAC:
                    TARGET_MAC = mac
                    #print(f"[✔] TARGET_MAC updated: {TARGET_MAC}", flush=True)

                    # update_total_bottles_for_current_user()
                    # sync_firestore_to_realtime()

                #else:
                    #print(f"[*] TARGET_MAC remains the same: {TARGET_MAC}", flush=True)
            else:
                if TARGET_MAC is not None:
                    #print("[*] No valid user found. Clearing TARGET_MAC.", flush=True)
                    TARGET_MAC = None

            time.sleep(1)
        except Exception as outer_err:
            #print(f"[!] Firestore monitoring error: {outer_err}", flush=True)
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
def update_user_by_mac(mac_address, bottle_size):
    try:
        # Sanitize MAC for Firebase keys
        mac_sanitized = mac_address.replace(":", "-")

        # Step 1: Check Firestore queuePosition
        firestore_user = db.collection('Users Collection').document(mac_address).get()
        if not firestore_user.exists:
            print(f"[!] User {mac_address} not found in Firestore.")
            return

        firestore_data = firestore_user.to_dict()
        queue_position = firestore_data.get('queuePosition', -1)

        if queue_position != 1:
            print(f"[!] Skipping update — User {mac_address} is not at queue position 1.")
            return

        # Step 2: Fetch current values from Realtime DB
        user_ref = realtime_db.reference(f'users/{mac_sanitized}')
        user_data = user_ref.get()

        if not user_data:
            print(f"[!] No user data found in Realtime DB for {mac_address}")
            return

        current_bottles = user_data.get('TotalBottlesDeposited', 0)
        current_wifi = user_data.get('WiFiTimeAvailable', 0)

        # Step 3: Determine Wi-Fi time increment based on bottle size
        wifi_time_increment = 5 * 60  # Default to 5 minutes for small bottle
        if bottle_size == 'large':
            wifi_time_increment = 10 * 60  # 10 minutes for large bottle

        # Increment the values
        new_bottles = current_bottles + 1
        new_wifi = current_wifi + wifi_time_increment

        # Step 4: Update Realtime DB with new values
        user_ref.update({
            'TotalBottlesDeposited': new_bottles,
            'WiFiTimeAvailable': new_wifi
        })

        print(f"[✓] Updated user {mac_address} - Bottles: {new_bottles}, WiFi Time: {new_wifi} seconds")

    except Exception as e:
        print(f"[!] Failed to update user by MAC: {e}")

#----------------------------Main detection------------------------

#bottle_model = YOLO('detect/train11/weights/best.pt')
bottle_model = YOLO('detect/train12/weights/best.pt')

esp32_cam_url = "http://192.168.8.101:81/stream"
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
        time.sleep(0.01)

thread = threading.Thread(target=capture_frames, daemon=True)
thread.start()

display_message("\nInsert bottle")

last_detection_time = time.time()
last_servo_position = None

def set_servo_position(pos):
    global last_servo_position
    if last_servo_position != pos:
        move_servo(pos)
        last_servo_position = pos

# Wait for object to approach
try:
    while True:
        dist = get_distance()
        if dist and dist < 14:
            print(f"✅ Object detected at {dist} cm...")
            break
        time.sleep(0.2)

    while True:
        # if frame is None:
        #     continue

        # dist = get_distance()
        # if not dist or dist > 14:
        #     display_message("Insert bottle")
        #     set_servo_position(0.5)  # Idle position
        #     time.sleep(0.2)
        #     continue
        dist = get_distance()

        if not dist:
            continue  # skip if reading failed

        if dist > 14:
            display_message("\nInsert bottle")
            set_servo_position(0.5)
            time.sleep(0.2)
            continue  # skip detection

        display_message("\nAnalyzing Object")
        time.sleep(5)

        # Check if the object is still there after waiting
        dist = get_distance()
        if not dist or dist > 14:
            print("❌ Object disappeared during analysis window. Skipping credit.")
            display_message("Rejected Bottle")
            set_servo_position(0)  # Reject
            time.sleep(2)
            set_servo_position(0.5)
            continue  # Restart loop

        # If still present, proceed with detection
        if frame is None:
            continue

        current_time = time.time()
        if current_time - last_detection_time >= 5:
            results = bottle_model(frame)[0]
            bottle_detected = False
            bottle_size = None

            if results.boxes is not None and len(results.boxes) > 0:
                frame_height, frame_width, _ = frame.shape

                for box in results.boxes:
                    confidence = box.conf[0].item()
                    if confidence >= 0.75:
                        class_id = int(box.cls[0])
                        class_name = bottle_model.names[class_id].lower()

                        x1, y1, x2, y2 = box.xyxy[0]
                        box_width = x2 - x1
                        box_height = y2 - y1
                        box_area = box_width * box_height
                        frame_area = frame_width * frame_height
                        percentage = (box_area / frame_area) * 100

                        print(f"🧠 Detected object: {class_name} | Confidence: {confidence*100:.2f}% | Area: {percentage:.2f}% of frame")

                        if class_name == "small_bottle":
                            bottle_detected = True
                            bottle_size = 'small'
                            break
                        elif class_name == "large_bottle":
                            bottle_detected = True
                            bottle_size = 'large'
                            break

            if bottle_detected:
                update_user_by_mac(TARGET_MAC, bottle_size)
                display_message("Accepting Bottle")

                if bottle_size == 'small':
                    WiFiTimeAvailable += 5 * 60
                    TotalBottlesDeposited += 1
                    print("[+] Small bottle detected: +5 mins Wi-Fi")
                elif bottle_size == 'large':
                    WiFiTimeAvailable += 10 * 60
                    TotalBottlesDeposited += 1
                    print("[+] Large bottle detected: +10 mins Wi-Fi")

                try:
                    result = update_user_by_mac(TARGET_MAC, TotalBottlesDeposited, WiFiTimeAvailable)
                    if not result:
                        print("❗ update_user_by_mac failed or returned no result.")
                except Exception as e:
                    print(f"❌ Exception in update_user_by_mac: {e}")

                set_servo_position(1)
                time.sleep(2)
                set_servo_position(0.5)

            else:
                print("❌ Object detected but not a valid bottle.")
                display_message("Rejected Bottle")
                set_servo_position(0)
                time.sleep(2)
                set_servo_position(0.5)

            last_detection_time = current_time


except KeyboardInterrupt:
    print("🛑 Exiting gracefully...")


finally:
    cap.release()
    GPIO.cleanup()
    cv2.destroyAllWindows()
    set_servo_position(0.5)
    stop_servo()
