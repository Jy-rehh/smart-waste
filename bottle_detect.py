import threading
import time
import cv2
from ultralytics import YOLO
from time import sleep

from servo import move_servo, stop_servo
from lcd import display_message

#model = YOLO('yolov8n.pt')
model = YOLO('detect/train10/weights/best.pt')
esp32_cam_url = "http://192.168.8.105:81/stream"
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

# Initial LCD message
display_message("Insert bottle")

# ========================
# 1. Only detect every 5s
# 2. Prevent servo jitter by only moving if needed
# ========================

last_detection_time = time.time()
last_servo_position = None  # Track last position to avoid jitter

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
            results = model(frame)[0]

            accept = False
            reject = False

            # If no detections at all, stay neutral
            if not results.boxes:
                move_servo(2)  # Neutral
            else:
                for box in results.boxes:
                    confidence = box.conf[0].item()
                    if confidence < 0.7:
                        reject = True  # below threshold
                        continue

                    class_id = int(box.cls[0])
                    class_name = model.names[class_id].lower()

                    if class_name in ["small_bottle", "large_bottle"]:
                        accept = True
                    else:
                        reject = True

                # Priority: Accept > Reject > Neutral
                if accept:
                    move_servo(1)  # Accept (left)
                elif reject:
                    move_servo(0)  # Reject (right)
                else:
                    move_servo(2)  # Neutral (center)


            if accept:
                display_message("Accepting Bottle")
                set_servo_position(1)  # accept area
                sleep(1.5)
                set_servo_position(0.5)  # neutral
                display_message("Insert bottle")

            elif reject and not only_background:
                display_message("Rejected Bottle")
                set_servo_position(0)  # reject area
                sleep(1.5)
                set_servo_position(0.5)  # neutral
                display_message("Insert bottle")

            elif only_background:
                display_message("Only Background - Idle")
                set_servo_position(0.5)  # neutral

            last_detection_time = current_time

        cv2.imshow("Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

except KeyboardInterrupt:
    print("🛑 Exiting gracefully...")

finally:
    cap.release()
    cv2.destroyAllWindows()
    stop_servo()
