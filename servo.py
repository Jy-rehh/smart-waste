import pigpio
from time import sleep

# Setup pigpio for PWM control
pi = pigpio.pi()
if not pi.connected:
    print("❌ Failed to connect to pigpio daemon.")
    exit()

servo_pin = 17
pi.set_mode(servo_pin, pigpio.OUTPUT)

# Function to move the servo based on position
def move_servo(position):
    print(f"Moving servo to position {position}")
    pulsewidth = int(500 + (position * 2000))
    pi.set_servo_pulsewidth(servo_pin, pulsewidth)
    sleep(2)  # Sleep for 2 seconds to allow servo to move
    pi.set_servo_pulsewidth(servo_pin, 0)  # Stop the servo

print("Testing servo movement...")
move_servo(1)  # Move to accepting position
move_servo(0)  # Move to rejecting position
move_servo(0.5)  # Reset to middle position
print("Servo test complete.")
