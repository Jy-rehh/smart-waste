# servo.py
import RPi.GPIO as GPIO
from time import sleep

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(16, GPIO.OUT)

pwm = GPIO.PWM(16, 50)
pwm.start(0)

def set_servo_position(position):
    # position: 0 = reject, 0.5 = neutral, 1 = accept
    if position == 1:
        pwm.ChangeDutyCycle(12.5)  # Accept
    elif position == 0:
        pwm.ChangeDutyCycle(2.5)   # Reject
    else:
        pwm.ChangeDutyCycle(7.5)   # Neutral
    sleep(0.5)

def stop_servo():
    pwm.stop()
    GPIO.cleanup()
