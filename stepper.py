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

# CORRECTED STEP SEQUENCES (SWAPPED CW/CCW)
step_sequence_cw = [
    [1, 0, 0, 1],  # (Originally Step 8)
    [0, 0, 0, 1],  # (Originally Step 7)
    [0, 0, 1, 1],  # (Originally Step 6)
    [0, 0, 1, 0],  # (Originally Step 5)
    [0, 1, 1, 0],  # (Originally Step 4)
    [0, 1, 0, 0],  # (Originally Step 3)
    [1, 1, 0, 0],  # (Originally Step 2)
    [1, 0, 0, 0]   # (Originally Step 1)
]

step_sequence_ccw = [
    [1, 0, 0, 0],  # (Originally Step 1)
    [1, 1, 0, 0],  # (Originally Step 2)
    [0, 1, 0, 0],  # (Originally Step 3)
    [0, 1, 1, 0],  # (Originally Step 4)
    [0, 0, 1, 0],  # (Originally Step 5)
    [0, 0, 1, 1],  # (Originally Step 6)
    [0, 0, 0, 1],  # (Originally Step 7)
    [1, 0, 0, 1]   # (Originally Step 8)
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
    print("Rotating CLOCKWISE (should turn RIGHT)...")
    move_steps(512, 0.005, "cw")  # Should now physically turn CW (right)
    time.sleep(1)
    
    print("Rotating COUNTER-CLOCKWISE (should turn LEFT)...")
    move_steps(512, 0.005, "ccw")  # Should now physically turn CCW (left)
    
    print("Test complete.")

finally:
    GPIO.cleanup()