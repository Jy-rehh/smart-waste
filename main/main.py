from ultralytics import YOLO 
import cvzone
import cv2

# Load the YOLO model
model = YOLO('yolov10n.pt')  # Make sure you have this model file
print(model.names)

# Use the ESP32-CAM MJPEG Stream URL
esp32_cam_url = "http://192.168.1.11:81/stream"  # Update with your ESP32-CAM's IP
cap = cv2.VideoCapture(esp32_cam_url)

if not cap.isOpened():
    print("Failed to connect to ESP32-CAM. Check the IP and Wi-Fi connection.")
    exit()

while True:
    ret, image = cap.read()
    if not ret:
        print("Failed to grab frame. Retrying...")
        continue
    
    # Run YOLO object detection
    results = model(image)
    for info in results:
        parameters = info.boxes
        for box in parameters:
            x1, y1, x2, y2 = box.xyxy[0].numpy().astype('int')
            confidence = int(box.conf[0].numpy() * 100)
            class_detected_number = int(box.cls[0])
            class_detected_name = model.names[class_detected_number]

            # Draw bounding box and label
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 3)
            cvzone.putTextRect(image, f'{class_detected_name} {confidence}%', 
                               [x1 + 8, y1 - 12], thickness=2, scale=1.5)

    # Show the result
    cv2.imshow('ESP32-CAM Object Detection', image)
    if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
        break

cap.release()
cv2.destroyAllWindows()
