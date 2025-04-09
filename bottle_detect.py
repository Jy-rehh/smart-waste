import threading
import cv2
import serial
import time
from ultralytics import YOLO
from gpiozero import Servo
import matplotlib.pyplot as plt

# Serial connection to Arduino (if needed)
# arduino = serial.Serial('COM5', 9600, timeout=1)
# time.sleep(2)  # Wait for Arduino to be ready

# Initialize the servo pin on the Raspberry Pi (GPIO pin 17 is used here, adjust as needed)
servo = Servo(17)

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
        servo.value = -1  # Move servo to the left (adjust value based on your servo setup)
        print(f"✅ {detected_label} detected. Servo moved to the left.")
    elif non_plastic_detected:
        detected_label = "NON_PLASTIC"
        servo.value = 1  # Move servo to the right (adjust value based on your servo setup)
        print(f"❌ {detected_label} detected. Servo moved to the right.")

    # Show the frame using matplotlib
    plt.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    plt.axis('off')  # Hide the axis
    plt.show(block=False)
    plt.pause(0.001)  # Pause to allow the plot to update

    # Optional: Send label to Arduino (if needed)
    # current_time = time.time()
    # if detected_label and (current_time - last_sent_time) >= detection_cooldown:
    #     arduino.write((detected_label + "\n").encode())
    #     print(f"✅ {detected_label} sent to Arduino.")
    #     last_sent_time = current_time

    # Wait for a short time before processing the next frame
    time.sleep(0.1)

# Cleanup
cap.release()
# arduino.close()  # Close the serial connection if used
