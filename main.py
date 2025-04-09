from ultralytics import YOLO
import cvzone
import cv2

model = YOLO("yolov10n.pt")
print("Model loaded:", model.names)

esp32_cam_url = "http://192.168.1.11:81/stream"
cap = cv2.VideoCapture(esp32_cam_url)

def generate_frames():
    while True:
        success, frame = cap.read()
        if not success:
            continue

        results = model(frame)
        for info in results:
            parameters = info.boxes
            for box in parameters:
                x1, y1, x2, y2 = box.xyxy[0].numpy().astype('int')
                confidence = int(box.conf[0].numpy() * 100)
                class_detected_number = int(box.cls[0])
                class_detected_name = model.names[class_detected_number]

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cvzone.putTextRect(frame, f'{class_detected_name} {confidence}%',
                                   [x1, y1 - 10], thickness=2, scale=1)

        # Convert frame to JPEG for streaming
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
