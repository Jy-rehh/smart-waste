import RPi.GPIO as GPIO
import time

# Define GPIO pins
IN1 = 17
IN2 = 18
IN3 = 27
IN4 = 22

# Set up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)

# Define the sequence for half-stepping
step_sequence = [
    [1,0,0,1],
    [1,0,0,0],
    [1,1,0,0],
    [0,1,0,0],
    [0,1,1,0],
    [0,0,1,0],
    [0,0,1,1],
    [0,0,0,1]
]

# Function to perform steps
def step_motor(steps, delay):
    for _ in range(steps):
        for step in step_sequence:
            GPIO.output(IN1, step[0])
            GPIO.output(IN2, step[1])
            GPIO.output(IN3, step[2])
            GPIO.output(IN4, step[3])
            time.sleep(delay)

try:
    print("Rotating motor...")
    step_motor(512, 0.001)  # 512 steps = 1 full rotation for 28BYJ-48
    print("Done!")

finally:
    GPIO.cleanup()
