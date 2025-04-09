from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

# Use the pigpio pin factory
factory = PiGPIOFactory()

# Initialize the servo on the GPIO pin, in this case, GPIO17
servo = Servo(17, pin_factory=factory)

# Sweep the servo back and forth
while True:
    servo.min()  # Move the servo to its minimum position
    sleep(1)
    servo.max()  # Move the servo to its maximum position
    sleep(1)
    servo.mid()  # Move the servo to its neutral/middle position
    sleep(1)
