import threading
import time
import cv2
from ultralytics import YOLO
from time import sleep

from servo import move_servo, stop_servo
from lcd import display_message

# ---------------- Wi-Fi Time Management ----------------
from librouteros import connect

# MikroTik Settings
ROUTER_HOST = '192.168.50.1'
ROUTER_USERNAME = 'admin'
ROUTER_PASSWORD = ''
TARGET_MAC = 'A2:DE:BF:8C:50:87'  # <<< Target device MAC address
USER_ID = USER_ID

# Connect to MikroTik
try:
    api = connect(username=ROUTER_USERNAME, password=ROUTER_PASSWORD, host=ROUTER_HOST)
    print("[*] Connected to MikroTik Router.")
except Exception as e:
    print(f"[!] MikroTik connection failed: {e}")
    exit()

bindings = api.path('ip', 'hotspot', 'ip-binding')

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

# Thread to manage WiFi time
def wifi_time_manager(user_id):
    global WiFiTimeAvailable

    current_binding = None

    user_ref = db.collection('Users').document(user_id)

    while True:
        # Fetch WiFiTimeAvailable from Firestore
        try:
            doc = user_ref.get()
            if doc.exists:
                data = doc.to_dict()
                WiFiTimeAvailable = data.get('WiFiTimeAvailable', 0)
        except Exception as e:
            print(f"[!] Failed to fetch WiFiTimeAvailable: {e}")

        if WiFiTimeAvailable > 0:
            if current_binding != 'bypassed':
                add_or_update_binding(TARGET_MAC, 'bypassed')
                current_binding = 'bypassed'

            WiFiTimeAvailable -= 1

            try:
                # Update WiFiTimeAvailable after decrement
                user_ref.update({'WiFiTimeAvailable': WiFiTimeAvailable})
            except Exception as e:
                print(f"[!] Failed to update WiFiTimeAvailable: {e}")

            time.sleep(1)

        else:
            if current_binding != 'regular':
                add_or_update_binding(TARGET_MAC, 'regular')
                current_binding = 'regular'

            time.sleep(5)

# Start the WiFi manager thread
threading.Thread(target=wifi_time_manager, daemon=True).start()
# ------------------------------------------------------



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

def set_servo_position(pos):
    global last_servo_position
    if last_servo_position != pos:
        move_servo(pos)
        last_servo_position = pos

try:
    while True:
        if frame is None:
            continue

        current_time = time.time()
        if current_time - last_detection_time >= 5:
            # Run both models
            bottle_results = bottle_model(frame)[0]
            general_results = general_model(frame)[0]

            # Flags
            bottle_detected = False
            general_detected = False

            # Check general model (e.g., to see if anything is there)
            if general_results.boxes is not None and len(general_results.boxes) > 0:
                general_detected = True

            # Check bottle model for accepted bottle types
            if bottle_results.boxes is not None and len(bottle_results.boxes) > 0:
                for box in bottle_results.boxes:
                    confidence = box.conf[0].item()
                    if confidence >= 0.7:
                        class_id = int(box.cls[0])
                        class_name = bottle_model.names[class_id].lower()
                        if class_name in ["small_bottle", "large_bottle"]:
                            bottle_detected = True
                            break

            # Decision logic
            neutral_classes = ["bottle", "toilet", "surfboard"]

            if bottle_detected:
                display_message("Accepting Bottle")

                # Update WiFi time and bottles count
                for box in bottle_results.boxes:
                    confidence = box.conf[0].item()
                    if confidence >= 0.7:
                        class_id = int(box.cls[0])
                        class_name = bottle_model.names[class_id].lower()

                    if class_name == "small_bottle":
                        WiFiTimeAvailable += 5 * 60
                        TotalBottlesDeposited += 1
                        update_user_data(user_id, TotalBottlesDeposited, WiFiTimeAvailable)
                        print("[+] Small bottle detected: +5 mins Wi-Fi")
                    elif class_name == "large_bottle":
                        WiFiTimeAvailable += 10 * 60
                        TotalBottlesDeposited += 1
                        update_user_data(user_id, TotalBottlesDeposited, WiFiTimeAvailable)
                        print("[+] Large bottle detected: +10 mins Wi-Fi")
                
                set_servo_position(1)  # Accept

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
                # Nothing in view, stay neutral
                set_servo_position(0.5)
                display_message("Insert bottle")
                continue

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
