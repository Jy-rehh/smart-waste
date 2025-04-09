import serial
import time
import RPi.GPIO as GPIO
import Adafruit_CharLCD as LCD  # Use Adafruit_CharLCD instead of lcddriver
from ultralytics import YOLO
import cv2

# Setup GPIO for Servo control
SERVO_PIN = 17  # GPIO pin for your servo
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Servo PWM setup
pwm = GPIO.PWM(SERVO_PIN, 50)  # 50Hz for standard servo
pwm.start(7.5)  # Neutral position (middle of servo's range)

# Setup LCD (Assumes you have a 16x2 LCD with I2C)
GPIO.setwarnings(False)  # Disable GPIO warnings
lcd = LCD.Adafruit_CharLCDPlate()  # Set up the LCD plate
lcd.clear()
lcd.message("LCD Initialized!")  # Test the LCD by showing a message

# Load YOLO model
model = YOLO('yolov8n.pt')

# Initialize serial connection to ESP32 on /dev/ttyUSB0
arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
time.sleep(2)  # Give it time to initialize

# Function to send data to the ESP32 (for testing)
def send_data_to_esp32(message):
    arduino.write(message.encode())

# ESP32-CAM stream URL (if you're also using it)
esp32_cam_url = "http://192.168.1.11:81/stream"  # Change to your ESP32's IP address
cap = cv2.VideoCapture(esp32_cam_url)

if not cap.isOpened():
    print("❌ Failed to connect to ESP32-CAM. Check IP or Wi-Fi.")
    exit()

# Shared frame variable
frame = None

# Function to keep capturing frames from ESP32-CAM
def capture_frames():
    global frame
    while True:
        ret, new_frame = cap.read()
        if ret:
            frame = new_frame

# Start frame capture thread
import threading
thread = threading.Thread(target=capture_frames, daemon=True)
thread.start()

# Main loop for detecting bottles
while True:
    if frame is None:
        continue  # Wait until frames are available

    # Run YOLO detection on the frame
    results = model(frame)

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

            if "bottle" in class_name.lower():
                plastic_detected = True
            else:
                non_plastic_detected = True

    if plastic_detected:
        detected_label = "PLASTIC"
    elif non_plastic_detected:
        detected_label = "NON_PLASTIC"

    if detected_label == "PLASTIC":
        print("✅ Plastic Bottle detected. Accepting...")
        pwm.ChangeDutyCycle(12.5)  # Move to 180° (accept position)
        time.sleep(2)
        pwm.ChangeDutyCycle(7.5)  # Return to neutral position
        lcd.clear()
        lcd.message("Plastic Bottle")
        send_data_to_esp32("PLASTIC DETECTED")

    elif detected_label == "NON_PLASTIC":
        print("❌ Non-Plastic detected. Rejecting...")
        pwm.ChangeDutyCycle(2.5)  # Move to 0° (reject position)
        time.sleep(2)
        pwm.ChangeDutyCycle(7.5)  # Return to neutral position
        lcd.clear()
        lcd.message("Non-Plastic")
        send_data_to_esp32("NON-PLASTIC DETECTED")

    # Show frame
    cv2.imshow('ESP32-CAM Object Detection', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
pwm.stop()
GPIO.cleanup()
arduino.close()
