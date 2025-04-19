from ultralytics import YOLO
import cvzone
import cv2
import time

# Load the YOLO model
model = YOLO('yolov10n.pt')
print("Model loaded with classes:", model.names)

# ESP32-CAM MJPEG stream URL
esp32_cam_url = "http://10.0.0.244:81/stream"
cap = cv2.VideoCapture(esp32_cam_url)

# Check if the stream opens
if not cap.isOpened():
    print("Failed to connect to ESP32-CAM. Check the IP and Wi-Fi connection.")
    exit()

# Optional: improve performance by reducing frame resolution
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

# Known plastic-related class names (add or update as needed)
plastic_keywords = ['bottle', 'plastic', 'water bottle']

while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠️ Frame grab failed.")
        continue

    start_time = time.time()

    # YOLO inference
    results = model(frame, verbose=False)[0]

    detected_objects = []

    for box in results.boxes:
        x1, y1, x2, y2 = box.xyxy[0].int().tolist()
        conf = int(box.conf[0] * 100)
        class_id = int(box.cls[0])
        label = model.names[class_id]

        detected_objects.append(label)

        # Draw bounding box and label
        color = (0, 255, 0) if any(k in label.lower() for k in plastic_keywords) else (0, 0, 255)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cvzone.putTextRect(frame, f"{label} {conf}%", (x1, y1 - 10), scale=1, thickness=1)

    # Display detected object list with check marks
    for obj in detected_objects:
        if any(keyword in obj.lower() for keyword in plastic_keywords):
            print(f"✅ Detected: {obj}")
        else:
            print(f"❌ Detected: {obj}")

    # Show image
    cv2.imshow("ESP32-CAM Object Detection", frame)

    # Optional: print frame rate
    # print("FPS:", round(1 / (time.time() - start_time), 2))

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
