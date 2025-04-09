from gpiozero import Servo
from time import sleep
from gpiozero.pins.pigpio import PiGPIOFactory

# Use pigpio for better accuracy
factory = PiGPIOFactory()
servo = Servo(17, pin_factory=factory)  # GPIO 17

# Move the servo
servo.min()   # one end
sleep(1)
servo.mid()   # center
sleep(1)
servo.max()   # other end
sleep(1)
