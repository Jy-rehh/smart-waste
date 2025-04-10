import RPi.GPIO as GPIO
import time

# BCM pin definitions
IN1 = 17
IN2 = 18
IN3 = 27
IN4 = 22

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)

# Half-step sequence
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

# Move steps in a given direction
def step_motor(steps, delay, reverse=False):
    sequence = step_sequence[::-1] if reverse else step_sequence
    for _ in range(steps):
        for step in sequence:
            GPIO.output(IN1, step[0])
            GPIO.output(IN2, step[1])
            GPIO.output(IN3, step[2])
            GPIO.output(IN4, step[3])
            time.sleep(delay)

try:
    print("Servo-like sweep started...")
    
    delay = 0.0015  # Adjust for speed
    angle_90 = 128  # ~90 degrees

    # Move Left
    step_motor(angle_90, delay, reverse=True)
    
    # Return to Center
    step_motor(angle_90, delay, reverse=False)
    
    time.sleep(1)  # Pause before next sweep

    # Move Right
    step_motor(angle_90, delay, reverse=False)
    
    # Return to Center
    step_motor(angle_90, delay, reverse=True)

    print("Finished servo-like sweep.")

finally:
    GPIO.cleanup()
    print("GPIO cleaned up.")
