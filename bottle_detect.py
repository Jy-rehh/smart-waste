import threading
import time
import cv2
from ultralytics import YOLO
from time import sleep

from stepper import move_steps  # Assuming you have the stepper motor functions here
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

# Initial LCD message
display_message("Insert bottle")

# ========================
# 1. Only detect every 5s
# 2. Prevent stepper jitter by only moving if needed
# ========================

last_detection_time = time.time()
last_stepper_position = None  # Track last position to avoid jitter

def set_stepper_position(pos):
    global last_stepper_position
    if last_stepper_position != pos:
        if pos == "accept":
            move_steps(512, 0.0015, "forward")  # 180° to accept position
        elif pos == "reject":
            move_steps(256, 0.0015, "backward")  # 90° to reject position
        last_stepper_position = pos

try:
    while True:
        if frame is None:
            continue

        current_time = time.time()
        if current_time - last_detection_time >= 5:
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
                display_message("Plastic Bottle\nAccepting")
                set_stepper_position("accept")
                sleep(1.5)
                move_steps(512, 0.0015, "backward")  # Move back to center
                display_message("Insert bottle")

            elif non_plastic_detected:
                display_message("Not a Plastic\nBottle Rejecting")
                set_stepper_position("reject")
                sleep(1.5)
                move_steps(256, 0.0015, "forward")  # Move back to center
                display_message("Insert bottle")

            else:
                display_message("Insert bottle")

            last_detection_time = current_time

        # Show the current frame for debugging
        cv2.imshow("Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

except KeyboardInterrupt:
    print("🛑 Exiting gracefully...")

finally:
    cap.release()
    cv2.destroyAllWindows()
    # Make sure the stepper is at the resting position
    move_steps(512, 0.0015, "backward")  # Move back to center
