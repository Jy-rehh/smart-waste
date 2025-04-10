import RPi.GPIO as GPIO
import time

# Define GPIO pins
IN1 = 17  # GPIO 17 (Pin 11)
IN2 = 18  # GPIO 18 (Pin 12)
IN3 = 27  # GPIO 27 (Pin 13)
IN4 = 22  # GPIO 22 (Pin 15)

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)

# Clockwise (Forward) Sequence
step_sequence_forward = [
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1],
    [1, 0, 0, 1]
]

# Counter-Clockwise (Backward) Sequence = Reverse of Forward
step_sequence_backward = [
    [1, 0, 0, 1],
    [0, 0, 0, 1],
    [0, 0, 1, 1],
    [0, 0, 1, 0],
    [0, 1, 1, 0],
    [0, 1, 0, 0],
    [1, 1, 0, 0],
    [1, 0, 0, 0]
]

def move_steps(steps, delay=0.001, direction="forward"):
    sequence = step_sequence_forward if direction == "forward" else step_sequence_backward
    
    for _ in range(steps):
        for step in sequence:
            GPIO.output(IN1, step[0])
            GPIO.output(IN2, step[1])
            GPIO.output(IN3, step[2])
            GPIO.output(IN4, step[3])
            time.sleep(delay)

try:
    print("Testing clockwise (forward) rotation...")
    move_steps(512, 0.001, "forward")  # Rotate ~90° CW
    time.sleep(1)
    
    print("Testing counter-clockwise (backward) rotation...")
    move_steps(512, 0.001, "backward")  # Rotate ~90° CCW back to start
    
    print("Movement test complete.")

finally:
    GPIO.cleanup()
    print("GPIO cleaned up.")