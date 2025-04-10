import RPi.GPIO as GPIO
import time

# Set up GPIO for the second ultrasonic sensor
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

TRIG2 = 27  # GPIO Pin 27
ECHO2 = 22  # GPIO Pin 22

GPIO.setup(TRIG2, GPIO.OUT)
GPIO.setup(ECHO2, GPIO.IN)

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
        distance2 = get_distance(TRIG2, ECHO2)
        print(f"Sensor 2 Distance: {distance2} cm")

        # Logic for container full detection
        if distance2 < 10:  # If the distance is less than 10 cm, container is full
            print("Container 2 is full!")

        time.sleep(1)

except KeyboardInterrupt:
    print("Program stopped.")
    GPIO.cleanup()
