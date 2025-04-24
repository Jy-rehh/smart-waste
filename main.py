import threading
import time
import cv2
from ultralytics import YOLO
from time import sleep

from servo import move_servo, stop_servo
from lcd import display_message

# Load your custom bottle-detection model
bottle_model = YOLO('detect/train11/weights/best.pt')

# Load pre-trained YOLOv8n model (general-purpose, COCO dataset)
general_model = YOLO('yolov8n.pt')

esp32_cam_url = "http://192.168.8.104:81/stream"
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
            if bottle_detected:
                display_message("Accepting Bottle")
                set_servo_position(1)  # Accept
            elif general_detected:
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
