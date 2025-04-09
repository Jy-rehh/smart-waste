import cv2
from ultralytics import YOLO
import time

# Frame capture settings
frame_skip = 3  # Skip every 3 frames to reduce processing load

# Load YOLO model
model = YOLO('yolov8n.pt')

# ESP32-CAM stream URL
esp32_cam_url = "http://192.168.1.11:81/stream"
cap = cv2.VideoCapture(esp32_cam_url)

if not cap.isOpened():
    print("❌ Failed to connect to ESP32-CAM. Check IP or Wi-Fi.")
    exit()

frame_count = 0

# Function to generate frames for Flask streaming
def generate_frames(socketio):
    global frame_count
    while True:
        ret, frame = cap.read()
        if not ret:
            continue  # Skip if frame not read correctly
        
        # Every 'frame_skip' frames, run detection and send the frame
        if frame_count % frame_skip == 0:
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

            # Encode the frame and send to the client
            ret, jpeg = cv2.imencode('.jpg', frame)
            if ret:
                frame_bytes = jpeg.tobytes()
                socketio.emit('video', frame_bytes)  # Send the frame via WebSocket

        frame_count += 1
