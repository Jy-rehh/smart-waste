import RPi.GPIO as GPIO
import time

# GPIO pin assignments
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

# Move a number of steps in a given direction
def move_steps(steps, delay, direction):
    seq = step_sequence[::-1] if direction == "backward" else step_sequence
    for _ in range(steps):
        for step in seq:
            GPIO.output(IN1, step[0])
            GPIO.output(IN2, step[1])
            GPIO.output(IN3, step[2])
            GPIO.output(IN4, step[3])
            time.sleep(delay)

try:
    print("Sweeping from left → center → right...")

    delay = 0.0012  # Speed (lower is faster)
    angle_90 = 128
    angle_180 = 256

    # Start at center
    # Move to left (backward 90°)
    move_steps(angle_90, delay, "backward")

    # Sweep smoothly to right (forward 180°)
    move_steps(angle_180, delay, "forward")

    # (Optional: Return to center)
    move_steps(angle_90, delay, "backward")

    print("Done!")

finally:
    GPIO.cleanup()
    print("GPIO cleaned up.")
