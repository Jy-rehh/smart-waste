import RPi.GPIO as GPIO
import time

# Define GPIO pins
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

# Function to move steps
def move_steps(step_count, delay, direction):
    sequence = step_sequence[::-1] if direction == "backward" else step_sequence
    for _ in range(step_count):
        for step in sequence:
            GPIO.output(IN1, step[0])
            GPIO.output(IN2, step[1])
            GPIO.output(IN3, step[2])
            GPIO.output(IN4, step[3])
            time.sleep(delay)

try:
    print("Stepper acting like servo...")

    delay = 0.0015
    angle_90 = 128  # 90 degrees
    angle_180 = 256  # 180 degrees

    # Center is assumed to be 0 steps from boot

    # Move left (−90°)
    move_steps(angle_90, delay, "backward")

    # Return to center
    move_steps(angle_90, delay, "forward")

    time.sleep(1)

    # Move right (+180°)
    move_steps(angle_180, delay, "forward")

    # Return to center
    move_steps(angle_180, delay, "backward")

    print("Sweep complete.")

finally:
    GPIO.cleanup()
    print("GPIO cleaned up.")
