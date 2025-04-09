import threading
import time
import cv2
import RPi.GPIO as GPIO
from ultralytics import YOLO
import pigpio
from time import sleep

# Setup pigpio for PWM control
pi = pigpio.pi()
if not pi.connected:
    print("❌ Failed to connect to pigpio daemon.")
    exit()

servo_pin = 17
pi.set_mode(servo_pin, pigpio.OUTPUT)

# LCD setup (same as before)
import smbus
I2C_ADDR = 0x27
bus = smbus.SMBus(1)
LCD_WIDTH = 16

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

def display_message(message):
    lcd_string(message, 0)  # Display message on the first line

# Load YOLO model
model = YOLO('yolov8n.pt')
esp32_cam_url = "http://192.168.1.11:81/stream"
cap = cv2.VideoCapture(esp32_cam_url)

if not cap.isOpened():
    print("❌ Failed to connect to ESP32-CAM. Check IP or Wi-Fi.")
    exit()

frame = None
last_sent_time = 0
detection_cooldown = 5  # Seconds between sending detections

# Start capturing frames
def capture_frames():
    global frame
    while True:
        ret, new_frame = cap.read()
        if ret:
            frame = new_frame

thread = threading.Thread(target=capture_frames, daemon=True)
thread.start()

# Function to move the servo based on detection
def move_servo(position):
    pulsewidth = int(500 + (position * 2000))
    pi.set_servo_pulsewidth(servo_pin, pulsewidth)

# Default message
display_message("Insert Bottle!")
time.sleep(2)

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
