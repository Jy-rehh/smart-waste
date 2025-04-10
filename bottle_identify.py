import RPi.GPIO as GPIO
import time

# Use BCM pin numbering
GPIO.setmode(GPIO.BCM)

# Define GPIO pins for TRIG and ECHO
TRIG = 23
ECHO = 24

print("Distance Measurement In Progress")

# Set up the GPIO pins
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# Ensure TRIG is low initially
GPIO.output(TRIG, False)
print("Waiting For Sensor To Settle")
time.sleep(2)

# Send a 10µs pulse to trigger the sensor
GPIO.output(TRIG, True)
time.sleep(0.00001)
GPIO.output(TRIG, False)

# Wait for the echo start
while GPIO.input(ECHO) == 0:
    pulse_start = time.time()

# Wait for the echo end
while GPIO.input(ECHO) == 1:
    pulse_end = time.time()

# Calculate pulse duration
pulse_duration = pulse_end - pulse_start

# Calculate distance (speed of sound is ~34300 cm/s)
distance = pulse_duration * 17150
distance = round(distance, 2)

print("Distance:", distance, "cm")

# Clean up GPIO settings
GPIO.cleanup()
