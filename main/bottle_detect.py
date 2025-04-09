import threading
import cv2
import time
from ultralytics import YOLO
import RPi.GPIO as GPIO
import smbus2
import lcddriver  # Assuming this is installed correctly
import Adafruit_CharLCD as LCD  # LCD display library

# Setup GPIO for Servo control
SERVO_PIN = 17  # GPIO pin for your servo
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Servo PWM setup
pwm = GPIO.PWM(SERVO_PIN, 50)  # 50Hz for standard servo
pwm.start(7.5)  # Neutral position (middle of servo's range)

# Setup LCD (Assumes you have a 16x2 LCD with I2C)
lcd = lcddriver.lcd()

# Load YOLO model
model = YOLO('yolov8n.pt')

# ESP32-CAM stream URL
esp32_cam_url = "http://192.168.1.11:81/stream"  # Update with the correct IP
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
    elif non_plastic_detected:
        detected_label = "NON_PLASTIC"

    # Control the servo based on detection label
    if detected_label == "PLASTIC":
        print("✅ Plastic Bottle detected. Accepting...")
        pwm.ChangeDutyCycle(12.5)  # Move to 180° (accept position)
        time.sleep(2)
        pwm.ChangeDutyCycle(7.5)  # Return to neutral position
        lcd.lcd_clear()
        lcd.lcd_display_string("Plastic Bottle", 1)
    elif detected_label == "NON_PLASTIC":
        print("❌ Non-Plastic detected. Rejecting...")
        pwm.ChangeDutyCycle(2.5)  # Move to 0° (reject position)
        time.sleep(2)
        pwm.ChangeDutyCycle(7.5)  # Return to neutral position
        lcd.lcd_clear()
        lcd.lcd_display_string("Non-Plastic", 1)

    # Show frame
    cv2.imshow('ESP32-CAM Object Detection', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
pwm.stop()
GPIO.cleanup()
