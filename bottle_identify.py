import RPi.GPIO as GPIO
import time

# Set up GPIO for the first ultrasonic sensor
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

TRIG1 = 23  # GPIO Pin 23
ECHO1 = 24  # GPIO Pin 24

GPIO.setup(TRIG1, GPIO.OUT)
GPIO.setup(ECHO1, GPIO.IN)

def get_distance(TRIG, ECHO):
    # Send a pulse to the TRIG pin
    GPIO.output(TRIG, GPIO.LOW)
    time.sleep(0.5)
    GPIO.output(TRIG, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIG, GPIO.LOW)

    # Measure the pulse duration from the ECHO pin
    while GPIO.input(ECHO) == GPIO.LOW:
        pulse_start = time.time()

    while GPIO.input(ECHO) == GPIO.HIGH:
        pulse_end = time.time()

    # Calculate the distance in cm
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)

    return distance

try:
    while True:
        distance1 = get_distance(TRIG1, ECHO1)
        print(f"Sensor 1 Distance: {distance1} cm")

        # Logic for bottle detection
        if distance1 < 5:  # If the distance is less than 5 cm, a bottle is close
            print("Bottle detected!")

        time.sleep(1)

except KeyboardInterrupt:
    print("Program stopped.")
    GPIO.cleanup()
