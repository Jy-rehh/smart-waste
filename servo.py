import pigpio
from time import sleep

# Setup pigpio for PWM control
pi = pigpio.pi()
if not pi.connected:
    print("❌ Failed to connect to pigpio daemon.")
    exit()

servo_pin = 17
pi.set_mode(servo_pin, pigpio.OUTPUT)

def move_servo(position):
    """
    Move servo to a specific position.
    Position ranges from 0 (0 degrees) to 1 (180 degrees).
    """
    pulsewidth = int(500 + (position * 2000))  # Calculate pulse width
    pi.set_servo_pulsewidth(servo_pin, pulsewidth)

def stop_servo():
    """Stop the servo movement and reset the pulse width."""
    pi.set_servo_pulsewidth(servo_pin, 0)
    pi.stop()

# Example usage:
# Move servo to 0 (accepting position)
move_servo(1)  # 1 means 180 degrees
sleep(1)

# Move servo to middle position (neutral)
move_servo(0.5)
sleep(1)

# Move servo to 0 (rejecting position)
move_servo(0)  # 0 means 0 degrees
sleep(1)

# Stop the servo
stop_servo()
