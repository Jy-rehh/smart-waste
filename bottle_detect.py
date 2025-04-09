import threading
import time
import cv2
from ultralytics import YOLO
from time import sleep

from servo import move_servo, stop_servo
from lcd import display_message

model = YOLO('yolov8n.pt')
esp32_cam_url = "http://192.168.1.11:81/stream"
cap = cv2.VideoCapture(esp32_cam_url)

if not cap.isOpened():
    print("❌ Failed to connect to ESP32-CAM. Check IP or Wi-Fi.")
    exit()

frame = None

# Start video capture thread
def capture_frames():
    global frame
    while True:
        ret, new_frame = cap.read()
        if ret:
            frame = new_frame

thread = threading.Thread(target=capture_frames, daemon=True)
thread.start()

last_action_time = time.time()

# Display "Insert Bottle" at startup
display_message("Insert bottle")

# Detection loop
while True:
    if frame is None:
        continue

    results = model(frame)
    plastic_detected = False
    non_plastic_detected = False

    for info in results:
        for box in info.boxes:
            confidence = box.conf[0].item()
            if confidence < 0.5:
                continue

            class_id = int(box.cls[0])
            class_name = model.names[class_id]

            if "bottle" in class_name.lower():
                plastic_detected = True
            else:
                non_plastic_detected = True

    if plastic_detected:
        display_message("Plastic Bottle\nAccepting...")
        move_servo(1)
        sleep(2)
        move_servo(0.5)
        display_message("Insert bottle")

    elif non_plastic_detected:
        display_message("Not a Plastic\nRejecting...")
        move_servo(0)
        sleep(2)
        move_servo(0.5)
        display_message("Insert bottle")

    else:
        # Only refresh message every few seconds
        if time.time() - last_action_time > 5:
            display_message("Insert bottle")

    last_action_time = time.time()

    cv2.imshow("Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
stop_servo()
