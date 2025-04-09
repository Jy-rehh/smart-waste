import threading
import time
import cv2
import RPi.GPIO as GPIO
from ultralytics import YOLO
from gpiozero import Servo
from time import sleep
import smbus

# Setup GPIO pins for Servo control (Change pin number as needed)
servo_pin = 17  # Example GPIO pin for servo motor
servo = Servo(servo_pin)

# LCD I2C setup
I2C_ADDR = 0x27  # Replace with your LCD I2C address
bus = smbus.SMBus(1)
LCD_WIDTH = 16  # Maximum characters per line

# LCD Constants
LCD_CMD = 0
LCD_CHR = 1

def lcd_init():
    sleep(0.5)
    lcd_byte(0x33, LCD_CMD)
    lcd_byte(0x32, LCD_CMD)
    lcd_byte(0x06, LCD_CMD)
    lcd_byte(0x0C, LCD_CMD)
    lcd_byte(0x01, LCD_CMD)
    sleep(0.5)

def lcd_byte(bits, mode):
    bus.write_byte(I2C_ADDR, mode)
    bus.write_byte(I2C_ADDR, bits)
    bus.write_byte(I2C_ADDR, bits << 4)

def lcd_string(message, line):
    lcd_byte(0x80 | line, LCD_CMD)
    for i in range(LCD_WIDTH):
        if i < len(message):
            lcd_byte(ord(message[i]), LCD_CHR)
        else:
            lcd_byte(0x20, LCD_CHR)

# Function to display messages on LCD
def display_message(message):
    lcd_string(message, 0)  # Display message on the first line

# Load YOLO model for bottle detection
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

# Default message on the LCD
display_message("Insert Bottle!")
time.sleep(2)

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
        display_message("Plastic Bottle")
        sleep(1)
        display_message("Accepting...")
        servo.max()  # Move to accepting position
    elif non_plastic_detected:
        detected_label = "NON_PLASTIC"
        display_message("Not a Plastic")
        sleep(1)
        display_message("Rejecting...")
        servo.min()  # Move to rejecting position

    # Wait for servo to hold position for a while
    sleep(2)
    servo.value = None  # Reset to neutral position

    # Show frame (for debugging purposes)
    cv2.imshow('ESP32-CAM Object Detection', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
GPIO.cleanup()
