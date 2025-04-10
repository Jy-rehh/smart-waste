import RPi.GPIO as GPIO
import time

# Define BCM GPIO pins connected to IN1–IN4 of ULN2003
IN1 = 17  # GPIO17 (Pin 11)
IN2 = 18  # GPIO18 (Pin 12)
IN3 = 27  # GPIO27 (Pin 13)
IN4 = 22  # GPIO22 (Pin 15)

# Setup GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Setup GPIO pins as outputs
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)

# Half-step sequence for 28BYJ-48
step_sequence = [
    [1, 0, 0, 1],
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1]
]

# Step function
def step_motor(steps, delay):
    for _ in range(steps):
        for step in step_sequence:
            GPIO.output(IN1, step[0])
            GPIO.output(IN2, step[1])
            GPIO.output(IN3, step[2])
            GPIO.output(IN4, step[3])
            time.sleep(delay)

try:
    print("Starting motor rotation...")
    
    # Rotate 1 full turn clockwise
    step_motor(512, 0.002)  # Try 0.002 or 0.005 if it's not moving

    print("Done rotating!")

finally:
    GPIO.cleanup()
    print("GPIO cleaned up.")
