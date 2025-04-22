from ultralytics import YOLO

# Correct the path to your dataset YAML file
dataset_path = 'C:/smart-waste/dataset/data.yaml'  # Or use absolute path for testing

print("Starting training...")

# Load YOLOv8 model (you can use 'yolov8n.pt' or any other model)
model = YOLO('yolov8n.pt')

# Train the model
model.train(data=dataset_path, epochs=50)

print("Training completed.")
