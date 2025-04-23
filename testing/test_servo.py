import RPi.GPIO as GPIO
from time import sleep

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

SERVO_PIN = 16
GPIO.setup(SERVO_PIN, GPIO.OUT)

pwm = GPIO.PWM(SERVO_PIN, 50)  # 50Hz for typical servos
pwm.start(0)  # Start with 0 duty cycle

def set_angle(angle):
    # Converts angle (0 to 180) to duty cycle (2.5 to 12.5)
    duty = 2.5 + (angle / 18)
    pwm.ChangeDutyCycle(duty)
    sleep(0.5)

try:
    print("Moving servo to LEFT (-90°)")
    set_angle(0)       # Leftmost
    sleep(1)

    print("Moving servo to CENTER (0°)")
    set_angle(90)      # Center
    sleep(1)

    print("Moving servo to RIGHT (+90°)")
    set_angle(180)     # Rightmost
    sleep(1)

finally:
    print("Stopping PWM and cleaning up GPIO")
    pwm.ChangeDutyCycle(0)
    sleep(0.5)
    pwm.stop()
    GPIO.cleanup()
