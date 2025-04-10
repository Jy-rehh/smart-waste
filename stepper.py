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

# Half-step sequence for 28BYJ-48 (to move stepper motor)
step_sequence_forward = [
    [1, 0, 0, 1],
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1]
]

step_sequence_backward = [
    [0, 0, 0, 1],
    [0, 0, 1, 1],
    [0, 0, 1, 0],
    [0, 1, 1, 0],
    [0, 1, 0, 0],
    [1, 1, 0, 0],
    [1, 0, 0, 0],
    [1, 0, 0, 1]
]

# Function to move steps
def move_steps(step_count, delay, direction):
    if direction == "backward":
        sequence = step_sequence_backward  # Use backward sequence for counter-clockwise
    else:
        sequence = step_sequence_forward  # Use forward sequence for clockwise
    
    for _ in range(step_count):
        for step in sequence:
            GPIO.output(IN1, step[0])
            GPIO.output(IN2, step[1])
            GPIO.output(IN3, step[2])
            GPIO.output(IN4, step[3])
            time.sleep(delay)

try:
    print("Stepper acting like servo...")

    delay = 0.0015  # Delay between steps (adjust for speed)
    
    # Define the number of steps for 90 and 180 degrees (based on stepper motor's step count)
    angle_90 = 128  # 90 degrees (change based on actual motor characteristics)
    angle_180 = 256  # 180 degrees (change based on actual motor characteristics)

    # Center is assumed to be 0 steps from boot

    # Move counter-clockwise (−90°)
    move_steps(angle_90, delay, "backward")

    # Return to center (0°)
    move_steps(angle_90, delay, "forward")

    time.sleep(2)  # Wait a few seconds

    # Move clockwise (+180°)
    move_steps(angle_180, delay, "forward")

    # Return to center (0°)
    move_steps(angle_180, delay, "backward")

    print("Sweep complete.")

finally:
    GPIO.cleanup()
    print("GPIO cleaned up.")
