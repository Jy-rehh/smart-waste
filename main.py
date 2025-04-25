# main.py
import threading
import time
from servo import set_servo_position
from container_full import monitor_container, container_full

# Dummy imports – replace with actual YOLO logic
from ultralytics import YOLO
import cv2

# Load models
bottle_model = YOLO("bottle.pt")
general_model = YOLO("yolov8n.pt")

# Init camera
cap = cv2.VideoCapture("http://192.168.8.101:81/stream")

# Message display
def display_message(message):
    print("[DISPLAY]", message)

# Start ultrasonic thread
ultrasonic_thread = threading.Thread(target=monitor_container, daemon=True)
ultrasonic_thread.start()

# Frame handling
last_detection_time = 0

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        if container_full:
            set_servo_position(0.5)
            display_message("Container Full")
            time.sleep(1.5)
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
                display_message("Accepting Bottle")
                set_servo_position(1)

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
                    display_message("Insert bottle")
                    set_servo_position(0.5)
                else:
                    display_message("Reject Object")
                    set_servo_position(0)
            else:
                display_message("Insert bottle")
                set_servo_position(0.5)

            last_detection_time = current_time
            time.sleep(1.5)
            set_servo_position(0.5)
            display_message("Insert bottle")

except KeyboardInterrupt:
    print("Shutting down.")
finally:
    cap.release()
    set_servo_position(0.5)
