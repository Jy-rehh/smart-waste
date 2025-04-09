from ultralytics import YOLO
import cvzone
import cv2
import threading
import time

model = YOLO("yolov10n.pt")
print("Model loaded:", model.names)

# Stream from ESP32-CAM
esp32_cam_url = "http://192.168.1.11:81/stream"
cap = cv2.VideoCapture(esp32_cam_url)

frame_queue = []
frame_count = 0
skip_frames = 2  # Skip every nth frame

def process_frame(frame):
    results = model(frame)
    for info in results:
        parameters = info.boxes
        for box in parameters:
            x1, y1, x2, y2 = box.xyxy[0].numpy().astype('int')
            confidence = int(box.conf[0].numpy() * 100)
            class_detected_number = int(box.cls[0])
            class_detected_name = model.names[class_detected_number]

            # Draw bounding boxes and add text
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cvzone.putTextRect(frame, f'{class_detected_name} {confidence}%', [x1, y1 - 10], thickness=2, scale=1)
    return frame

def read_frames():
    global frame_count
    while True:
        success, frame = cap.read()
        if not success:
            continue
        
        # Skip frames based on the skip_frames value
        if frame_count % skip_frames == 0:
            frame = process_frame(frame)  # Process the frame with YOLO
            if len(frame_queue) < 10:  # Avoid overloading memory with too many frames
                frame_queue.append(frame)

        frame_count += 1

# Start the frame reading thread
frame_thread = threading.Thread(target=read_frames)
frame_thread.daemon = True
frame_thread.start()

def generate_frames():
    while True:
        if len(frame_queue) > 0:
            frame = frame_queue.pop(0)
            # Convert frame to JPEG for streaming
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
