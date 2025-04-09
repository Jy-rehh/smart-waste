import serial
import time
from time import sleep
import RPi.GPIO as GPIO

# Setup GPIO for Servo control
SERVO_PIN = 17  # Set the correct GPIO pin for your servo

GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Servo PWM setup (assuming a standard servo motor)
pwm = GPIO.PWM(SERVO_PIN, 50)  # 50Hz for standard servo
pwm.start(7.5)  # Neutral position (middle of servo's range)

# Serial connection to Arduino
arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
time.sleep(2)  # Wait for Arduino to be ready

while True:
    if arduino.in_waiting > 0:
        detection_label = arduino.readline().decode('utf-8').strip()

        if detection_label == "PLASTIC":
            print("✅ Plastic Bottle detected. Accepting...")
            pwm.ChangeDutyCycle(12.5)  # Move to 180° (accept position)
            sleep(2)  # Wait for the servo to move
            pwm.ChangeDutyCycle(7.5)  # Return to neutral position
        elif detection_label == "NON_PLASTIC":
            print("❌ Non-Plastic detected. Rejecting...")
            pwm.ChangeDutyCycle(2.5)  # Move to 0° (reject position)
            sleep(2)  # Wait for the servo to move
            pwm.ChangeDutyCycle(7.5)  # Return to neutral position

        sleep(1)  # Delay before checking for next input

# Cleanup
pwm.stop()
GPIO.cleanup()
