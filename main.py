# bottle_detect.py

import threading
import time
import cv2
from ultralytics import YOLO
from time import sleep
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)  # Set mode once here

from container_full import monitor_container, container_full
from bottle_detect import start_detection

# Start your app logic (just an example)
monitor_thread = threading.Thread(target=monitor_container, daemon=True)
monitor_thread.start()

start_detection()

from servo import move_servo, stop_servo
from lcd import display_message
from container_full import monitor_container, container_full

# Load models
bottle_model = YOLO('detect/train11/weights/best.pt')
general_model = YOLO('yolov8n.pt')

# Camera setup
esp32_cam_url = "http://192.168.8.104:81/stream"
cap = cv2.VideoCapture(esp32_cam_url)

if not cap.isOpened():
    print("❌ Failed to connect to ESP32-CAM. Check IP or Wi-Fi.")
    exit()

frame = None

# Thread to capture camera frames
def capture_frames():
    global frame
    while True:
        ret, new_frame = cap.read()
        if ret:
            frame = new_frame

# Start camera thread
threading.Thread(target=capture_frames, daemon=True).start()

# Start ultrasonic thread
threading.Thread(target=monitor_container, daemon=True).start()

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
            bottle_results = bottle_model(frame)[0]
            general_results = general_model(frame)[0]

            bottle_detected = False
            general_detected = False

            if general_results.boxes is not None and len(general_results.boxes) > 0:
                general_detected = True

            if bottle_results.boxes is not None and len(bottle_results.boxes) > 0:
                for box in bottle_results.boxes:
                    confidence = box.conf[0].item()
                    if confidence >= 0.7:
                        class_id = int(box.cls[0])
                        class_name = bottle_model.names[class_id].lower()
                        if class_name in ["small_bottle", "large_bottle"]:
                            bottle_detected = True
                            break

            neutral_classes = ["bottle", "toilet", "surfboard"]

            if bottle_detected:
                if container_full:
                    display_message("Bin Full. Try Later.")
                    set_servo_position(0)  # Reject
                else:
                    display_message("Accepting Bottle")
                    set_servo_position(1)  # Accept

            elif general_detected:
                go_neutral = False
                for box in general_results.boxes:
                    confidence = box.conf[0].item()
                    if confidence < 0.6:
                        continue
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
                set_servo_position(0.5)
                display_message("Insert bottle")

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
