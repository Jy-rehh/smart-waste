import RPi.GPIO as GPIO
from time import sleep

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(16, GPIO.OUT)

pwm = GPIO.PWM(16, 50)  # 50Hz
pwm.start(0)

def set_angle(angle):
    duty = 2.5 + (angle / 18)
    GPIO.output(16, True)
    pwm.ChangeDutyCycle(duty)
    sleep(1)
    GPIO.output(16, False)
    pwm.ChangeDutyCycle(0)

try:
    set_angle(0)
    set_angle(90)
    set_angle(180)
finally:
    pwm.stop()
    GPIO.cleanup()
