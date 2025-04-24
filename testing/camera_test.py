import threading
import time
import cv2
from ultralytics import YOLO

# ✅ Load your custom trained model (replace path with your actual path)
model = YOLO('detect/train11/weights/best.pt')

# ✅ ESP32-CAM MJPEG stream
esp32_cam_url = "http://192.168.8.104:81/stream"
cap = cv2.VideoCapture(esp32_cam_url)

if not cap.isOpened():
    print("❌ Failed to connect to ESP32-CAM. Check IP or Wi-Fi.")
    exit()

frame = None

# Capture video frames in a separate thread
def capture_frames():
    global frame
    printed_resolution = False  # ✅ To print only once
    while True:
        ret, new_frame = cap.read()
        if ret:
            frame = new_frame
            if not printed_resolution:
                print(f"📷 Frame resolution: {frame.shape[1]}x{frame.shape[0]}")
                printed_resolution = True

thread = threading.Thread(target=capture_frames, daemon=True)
thread.start()

last_detection_time = time.time()  # Stores recent detections
last_detections = []  # ✅ Add this line before the loop

try:
    while True:
        if frame is None:
            continue

        current_time = time.time()

        # ✅ Run detection every 1 second
        if current_time - last_detection_time >= 1:
            results = model(frame)[0]
            detections = []

            for box in results.boxes:
                x1, y1, x2, y2 = box.xyxy[0].int().tolist()
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                label = model.names[class_id]
                detections.append((x1, y1, x2, y2, label, confidence))
                print(f"🟢 Detected: {label} ({confidence:.2f})")

            last_detections = detections  # ✅ Update stored detections
            last_detection_time = current_time

        # ✅ Draw last known detections
        for x1, y1, x2, y2, label, confidence in last_detections:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{label} {confidence:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.imshow("YOLOv8 ESP32-CAM Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("🛑 Detection stopped manually.")

finally:
    cap.release()
    cv2.destroyAllWindows()
