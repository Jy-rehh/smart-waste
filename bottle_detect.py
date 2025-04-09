import threading
import cv2
import time
from ultralytics import YOLO
from gpiozero import Servo
from time import sleep

# Set up the Servo (GPIO pin 17 for example)
servo_left = Servo(17)  # Move left for plastic bottle
servo_right = Servo(18)  # Move right for non-plastic

# Load YOLO model
model = YOLO('yolov8n.pt')

# ESP32-CAM stream URL
esp32_cam_url = "http://192.168.1.11:81/stream"
cap = cv2.VideoCapture(esp32_cam_url)

if not cap.isOpened():
    print("❌ Failed to connect to ESP32-CAM. Check IP or Wi-Fi.")
    exit()

# Shared frame variable
frame = None
last_sent_time = 0
detection_cooldown = 5  # Seconds between sending detections

# Function to keep capturing frames
def capture_frames():
    global frame
    while True:
        ret, new_frame = cap.read()
        if ret:
            frame = new_frame

# Start frame capture thread
thread = threading.Thread(target=capture_frames, daemon=True)
thread.start()

while True:
    if frame is None:
        continue  # Wait until frames are available

    # Run YOLO detection on the frame
    results = model(frame)

    # Detection flags
    plastic_detected = False
    non_plastic_detected = False
    detected_label = ""

    for info in results:
        for box in info.boxes:
            confidence = box.conf[0].item()
            if confidence < 0.5:
                continue  # Skip low-confidence detections

            # Get coordinates and class name
            x1, y1, x2, y2 = box.xyxy[0].numpy().astype(int)
            class_id = int(box.cls[0])
            class_name = model.names[class_id]

            # Draw box and label on frame
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
            cv2.putText(frame, f'{class_name} {int(confidence * 100)}%',
                        (x1 + 8, y1 - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (255, 255, 255), 2)

            # Label detection
            if "bottle" in class_name.lower():
                plastic_detected = True
            else:
                non_plastic_detected = True

    # Decide label based on detection
    if plastic_detected:
        detected_label = "PLASTIC"
        servo_left.value = 1  # Move servo to the left
        servo_right.value = None  # Reset the right servo
    elif non_plastic_detected:
        detected_label = "NON_PLASTIC"
        servo_right.value = 1  # Move servo to the right
        servo_left.value = None  # Reset the left servo

    # Wait for the servo to move before detecting again
    sleep(1)  # Adjust as needed

    # Show frame
    cv2.imshow('ESP32-CAM Object Detection', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
