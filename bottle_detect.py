import threading
import time
import cv2
from ultralytics import YOLO
from time import sleep

from servo import move_servo, stop_servo
from lcd import display_message

# Load the model (no background class)
model = YOLO('detect/train11/weights/best.pt')

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
last_servo_position = None  # Track last position

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

            # If no detections, stay neutral
            if results.boxes is None or len(results.boxes) == 0:
                set_servo_position(0.5)  # Neutral
                display_message("Insert bottle")
            else:
                for box in results.boxes:
                    confidence = box.conf[0].item()
                    if confidence < 0.7:
                        reject = True
                        continue

                    class_id = int(box.cls[0])
                    class_name = model.names[class_id].lower()

                    if class_name in ["small_bottle", "large_bottle"]:
                        accept = True
                    else:
                        reject = True

                # Decision based on detection
                if accept:
                    display_message("Accepting Bottle")
                    set_servo_position(1)  # Accept
                    sleep(1.5)
                    set_servo_position(0.5)  # Neutral
                    display_message("Insert bottle")

                elif reject:
                    display_message("Rejected Bottle")
                    set_servo_position(0)  # Reject
                    sleep(1.5)
                    set_servo_position(0.5)  # Neutral
                    display_message("Insert bottle")

            last_detection_time = current_time

        # Optional: GUI output
       # if cv2.getWindowProperty("Detection", 0) >= 0:  # avoid crash if window closed
       #     cv2.imshow("Detection", frame)
       #     if cv2.waitKey(1) & 0xFF == ord("q"):
       #         break

except KeyboardInterrupt:
    print("🛑 Exiting gracefully...")

finally:
    cap.release()
    cv2.destroyAllWindows()
    stop_servo()
