import RPi.GPIO as GPIO
import time

# GPIO Pins (BCM numbering)
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
step_sequence_cw = [
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1],
    [1, 0, 0, 1]
]

# Counter-Clockwise (Backward) Sequence = REVERSE of CW
step_sequence_ccw = [
    [1, 0, 0, 1],
    [0, 0, 0, 1],
    [0, 0, 1, 1],
    [0, 0, 1, 0],
    [0, 1, 1, 0],
    [0, 1, 0, 0],
    [1, 1, 0, 0],
    [1, 0, 0, 0]
]

def move_steps(steps, delay=0.005, direction="cw"):
    sequence = step_sequence_cw if direction == "cw" else step_sequence_ccw
    
    for _ in range(steps):
        for step in sequence:
            GPIO.output(IN1, step[0])
            GPIO.output(IN2, step[1])
            GPIO.output(IN3, step[2])
            GPIO.output(IN4, step[3])
            time.sleep(delay)

try:
    print("Rotating CLOCKWISE (512 steps)...")
    move_steps(512, 0.005, "cw")  # CW rotation
    time.sleep(1)
    
    print("Rotating COUNTER-CLOCKWISE (512 steps)...")
    move_steps(512, 0.005, "ccw")  # CCW rotation
    
    print("Test complete.")

finally:
    GPIO.cleanup()