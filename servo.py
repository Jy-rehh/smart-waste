# # We imports the GPIO module
# import RPi.GPIO as GPIO
# # We import the command sleep from time
# from time import sleep

# # Stops all warnings from appearing
# GPIO.setwarnings(False)

# # We name all the pins on BOARD mode
# GPIO.setmode(GPIO.BOARD)
# # Set an output for the PWM Signal
# GPIO.setup(16, GPIO.OUT)

# # Set up the PWM on pin #16 at 50Hz
# pwm = GPIO.PWM(16, 50)
# pwm.start(0) # Start the servo with 0 duty cycle ( at 0 deg position )
# pwm.ChangeDutyCycle(5) # Tells the servo to turn to the left ( -90 deg position )
# sleep(0.5) # Tells the servo to Delay for 5sec
# pwm.ChangeDutyCycle(7.5) # Tells the servo to turn to the neutral position ( at 0 deg position )
# sleep(0.5) # Tells the servo to Delay for 5sec
# pwm.ChangeDutyCycle(10) # Tells the servo to turn to the right ( +90 deg position )
# sleep(0.5) # Tells the servo to Delay for 5sec
# pwm.stop(0) # Stop the servo with 0 duty cycle ( at 0 deg position )
# GPIO.cleanup() # Clean up all the ports we've used.

# servo.py
import RPi.GPIO as GPIO
from time import sleep

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(16, GPIO.OUT)

pwm = GPIO.PWM(16, 50)
pwm.start(0)

def move_servo(position):
    if position == 1:  # Accept
        pwm.ChangeDutyCycle(10)
    elif position == 0:  # Reject
        pwm.ChangeDutyCycle(5)
    else:  # Reset/Neutral
        pwm.ChangeDutyCycle(7.5)
    sleep(0.5)

def stop_servo():
    pwm.stop()
    GPIO.cleanup()
