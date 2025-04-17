import threading
import time
import cv2
from ultralytics import YOLO
from time import sleep
import RPi.GPIO as GPIO

from servo import move_servo, stop_servo
from lcd import display_message

# === YOLO model and ESP32-CAM setup ===
model = YOLO('yolov8n.pt')
esp32_cam_url = "http://192.168.1.10:81/stream"
cap = cv2.VideoCapture(esp32_cam_url)

if not cap.isOpened():
    print("❌ Failed to connect to ESP32-CAM. Check IP or Wi-Fi.")
    exit()

frame = None

# === Ultrasonic sensor setup ===
TRIG_PIN = 11  # GPIO11 (physical pin 23)
ECHO_PIN = 8   # GPIO8  (physical pin 24)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

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

# === Frame capture thread ===
def capture_frames():
    global frame
    while True:
        ret, new_frame = cap.read()
        if ret:
            frame = new_frame

thread = threading.Thread(target=capture_frames, daemon=True)
thread.start()

# === Initial UI state ===
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
                distance = get_distance()
                if distance is not None and distance < 5:  # 5cm threshold
                    display_message("Bin Full. Cannot Accept.")
                    set_servo_position(0)  # Reject position
                else:
                    display_message("Plastic Bottle Accepting")
                    set_servo_position(1)  # Accept
                    sleep(1.5)
                    set_servo_position(0.5)  # Neutral
                display_message("Insert bottle")

            elif non_plastic_detected:
                display_message("Not a Plastic Bottle Rejecting")
                set_servo_position(0)  # Reject
                sleep(1.5)
                set_servo_position(0.5)
                display_message("Insert bottle")

            else:
                display_message("Insert bottle")

            last_detection_time = current_time

        # Show frame for debugging
        cv2.imshow("Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

except KeyboardInterrupt:
    print("🛑 Exiting gracefully...")

finally:
    cap.release()
    cv2.destroyAllWindows()
    stop_servo()
    GPIO.cleanup()
