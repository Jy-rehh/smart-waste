import RPi.GPIO as GPIO
import time

# GPIO Pins (BCM numbering)
IN1 = 17
IN2 = 18
IN3 = 27
IN4 = 22

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)

# Correct Half-Step Sequence for 28BYJ-48
step_sequence = [
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1],
    [1, 0, 0, 1]
]

def move_steps(steps, delay=0.005, direction=1):
    for _ in range(steps):
        for i in range(8) if direction == 1 else range(7, -1, -1):
            step = step_sequence[i]
            GPIO.output(IN1, step[0])
            GPIO.output(IN2, step[1])
            GPIO.output(IN3, step[2])
            GPIO.output(IN4, step[3])
            time.sleep(delay)

try:
    print("Rotating CLOCKWISE (512 steps)...")
    move_steps(512, 0.005, 1)  # CW
    time.sleep(1)
    
    print("Rotating COUNTER-CLOCKWISE (512 steps)...")
    move_steps(512, 0.005, -1)  # CCW
    
    print("Test complete.")

finally:
    GPIO.cleanup()