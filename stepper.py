import RPi.GPIO as GPIO
import time

# GPIO pin setup (IN1, IN2, IN3, IN4 on ULN2003)
IN1 = 17
IN2 = 18
IN3 = 27
IN4 = 22

# Set up GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setup([IN1, IN2, IN3, IN4], GPIO.OUT)

# Define the sequence for 28BYJ-48 motor
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

steps_per_revolution = 4096  # 28BYJ-48 default

def move_steps(steps, direction=1, delay=0.002):
    for _ in range(abs(steps)):
        for step in step_sequence[::direction]:
            GPIO.output(IN1, step[0])
            GPIO.output(IN2, step[1])
            GPIO.output(IN3, step[2])
            GPIO.output(IN4, step[3])
            time.sleep(delay)

try:
    while True:
        print("Clockwise from home")
        move_steps(steps_per_revolution, direction=1)
        time.sleep(1)

        print("Back to home")
        move_steps(steps_per_revolution, direction=-1)
        time.sleep(1)

        print("Counterclockwise from home")
        move_steps(steps_per_revolution, direction=-1)
        time.sleep(1)

        print("Back to home")
        move_steps(steps_per_revolution, direction=1)
        time.sleep(1)

except KeyboardInterrupt:
    print("Stopped by user")

finally:
    GPIO.cleanup()
