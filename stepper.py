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

# Motor characteristics
STEPS_PER_REVOLUTION = 4096  # 28BYJ-48 has 4096 steps per revolution (in half-step mode)
STEPS_PER_DEGREE = STEPS_PER_REVOLUTION / 360  # ~11.377 steps per degree

# Global variable to track current position (in steps from zero)
current_position = 0

def move_to_angle(target_angle, delay=0.001):
    global current_position
    
    # Calculate target position in steps
    target_steps = int(target_angle * STEPS_PER_DEGREE)
    steps_to_move = target_steps - current_position
    
    if steps_to_move == 0:
        return  # Already at target position
    
    direction = "forward" if steps_to_move > 0 else "backward"
    step_count = abs(steps_to_move)
    
    # Execute the movement
    for _ in range(step_count):
        if direction == "forward":
            step = step_sequence[current_position % 8]
            current_position += 1
        else:
            step = step_sequence[(current_position - 1) % 8]
            current_position -= 1
        
        GPIO.output(IN1, step[0])
        GPIO.output(IN2, step[1])
        GPIO.output(IN3, step[2])
        GPIO.output(IN4, step[3])
        time.sleep(delay)

def return_to_zero(delay=0.001):
    global current_position
    move_to_angle(0, delay)

try:
    print("Stepper acting like servo...")
    
    # Initial delay between steps (adjust for speed)
    step_delay = 0.001
    
    # Move to zero position (if not already there)
    return_to_zero(step_delay)
    print("At zero position")
    
    # Move to -90° (counter-clockwise)
    move_to_angle(-90, step_delay)
    print("Moved to -90°")
    
    # Return to 0°
    return_to_zero(step_delay)
    print("Returned to 0°")
    
    time.sleep(2)  # Wait 2 seconds
    
    # Move to +180° (clockwise)
    move_to_angle(180, step_delay)
    print("Moved to +180°")
    
    # Return to 0°
    return_to_zero(step_delay)
    print("Returned to 0°")
    
    print("Sweep complete.")

finally:
    GPIO.cleanup()
    print("GPIO cleaned up.")