import cv2
import threading
import time
from ultralytics import YOLO
from gpiozero import Servo
import smbus
from flask import Flask, render_template, Response

# Initialize the servo
servo = Servo(17)

# Initialize the I2C bus and LCD
bus = smbus.SMBus(1)
LCD_ADDR = 0x27  # Default I2C address for most LCDs

# LCD Command Functions
def lcd_command(command):
    bus.write_byte(LCD_ADDR, command)
    time.sleep(0.001)

def lcd_write(message):
    for char in message:
        bus.write_byte(LCD_ADDR, ord(char))
        time.sleep(0.001)

def lcd_clear():
    lcd_command(0x01)  # Clear the display
    time.sleep(0.001)

# Load YOLO model
model = YOLO('yolov8n.pt')

# ESP32-CAM stream URL
esp32_cam_url = "http://192.168.1.11:81/stream"
cap = cv2.VideoCapture(esp32_cam_url)

if not cap.isOpened():
    print("❌ Failed to connect to ESP32-CAM. Check IP or Wi-Fi.")
    exit()

# Flask setup
app = Flask(__name__)

# Shared frame variable
frame = None

# Function to capture frames from ESP32-CAM
def capture_frames():
    global frame
    while True:
        ret, new_frame = cap.read()
        if ret:
            frame = new_frame

# Start frame capture thread
thread = threading.Thread(target=capture_frames, daemon=True)
thread.start()

# Function to generate frames for Flask streaming
def generate_frames():
    global frame
    while True:
        if frame is None:
            continue  # Wait for a frame to be available

        # Run YOLO detection on the frame
        results = model(frame)
        
        # Detection flags
        plastic_detected = False
        non_plastic_detected = False

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

        # Send the frame as a JPEG image
        ret, jpeg = cv2.imencode('.jpg', frame)
        if ret:
            frame_bytes = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')

# Flask route for video feed
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Flask route for the index page
@app.route('/')
def index():
    return render_template('index.html')

# Run Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
