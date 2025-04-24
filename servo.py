# servo.py
import RPi.GPIO as GPIO
from time import sleep

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(16, GPIO.OUT)

pwm = GPIO.PWM(16, 50)
pwm.start(0)

# def move_servo(position):
#     if position == 1:  # Accept
#         pwm.ChangeDutyCycle(10)
#     elif position == 0:  # Reject
#         pwm.ChangeDutyCycle(5)
#     else:  # Reset/Neutral
#         pwm.ChangeDutyCycle(7.5)
#     sleep(0.5)
def move_servo(position):
    if position == 1:  # Accept
        pwm.ChangeDutyCycle(12.5)  # Try for 180 deg
    elif position == 0:  # Reject
        pwm.ChangeDutyCycle(2.5)   # Try for 0 deg
    else:  # Neutral
        pwm.ChangeDutyCycle(7.5)   # 90 deg
    sleep(0.5)

def stop_servo():
     pwm.stop()
     GPIO.cleanup()

