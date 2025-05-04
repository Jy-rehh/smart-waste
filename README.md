# Smart Waste Smart Access

A Raspberry Pi-based system that classifies plastic bottles using a YOLOv8n model trained with Roboflow, and manages user interactions via a web interface served through a MikroTik WiFi network.

## System Overview

- **Hardware**: Raspberry Pi 4
-             : ESP32-CAM
-             : Ultrasonic Sensor
-             : Servo Motor
- **Machine Learning**: YOLOv8n model trained via Roboflow
- **Network**: MikroTik router providing WiFi access
- **User Flow**:
  1. User connects to designated WiFi
  2. Automatically redirected to web interface
     ![image](https://github.com/user-attachments/assets/fe54d21a-59fa-4c72-bd26-2b83b11f6fb3)
     
  4. Selects "Insert Bottle" option
     ![image](https://github.com/user-attachments/assets/7e62bf8c-bd51-4207-b784-2b5e32cc7284)
     
  6. Inserts bottle for classification
  7. Receives time credit based on bottle size:
     ![image](https://github.com/user-attachments/assets/9915ef65-2e4e-4409-a435-53313cdc437a)

## Setup Instructions

### Prerequisites
- Raspberry Pi 4
- Python 3.x
- MikroTik router with Hotspot configured
- RoboFlow account with trained YOLOv8n model

### Installation
