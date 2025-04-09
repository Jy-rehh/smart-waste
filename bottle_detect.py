import threading
import time
import cv2
from ultralytics import YOLO
import pigpio
import smbus
from time import sleep

# Import the servo and LCD control functions
from servo import move_servo, stop_servo
from lcd import display_message

# Setup YOLO model
model = YOLO('yolov8n.pt')
esp32_cam_url = "http://192.168.1.11:81/stream"
cap = cv2.VideoCapture(esp32_cam_url)

if not cap.isOpened():
    print("❌ Failed to connect to ESP32-CAM. Check IP or Wi-Fi.")
    exit()

frame = None

# Start capturing frames
def capture_frames():
    global frame
    while True:
        ret, new_frame = cap.read()
        if ret:
            frame = new_frame

thread = threading.Thread(target=capture_frames, daemon=True)
thread.start()

# Start detecting bottles
while True:
    if frame is None:
        continue  # Wait until frames are available

    results = model(frame)
    plastic_detected = False
    non_plastic_detected = False
    detected_label = ""

    for info in results:
        for box in info.boxes:
            confidence = box.conf[0].item()
            if confidence < 0.5:
                continue

            x1, y1, x2, y2 = box.xyxy[0].numpy().astype(int)
            class_id = int(box.cls[0])
            class_name = model.names[class_id]

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
            cv2.putText(frame, f'{class_name} {int(confidence * 100)}%',
                        (x1 + 8, y1 - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (255, 255, 255), 2)

            if "bottle" in class_name.lower():
                plastic_detected = True
            else:
                non_plastic_detected = True

    if plastic_detected:
        detected_label = "PLASTIC"
        display_message("Plastic Bottle")
        sleep(1)
        display_message("Accepting...")  # Ensure that it is updated clearly
        move_servo(1)  # Move to accepting position
    elif non_plastic_detected:
        detected_label = "NON_PLASTIC"
        display_message("Not a Plastic")
        sleep(1)
        display_message("Rejecting...")  # Ensure that it is updated clearly
        move_servo(0)  # Move to rejecting position

    sleep(2)  # Hold for 2 seconds
    move_servo(0.5)  # Reset servo to middle position

    if detected_label:
        last_sent_time = time.time()
    
    # Only update the frame display at the end
    cv2.imshow('Detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
