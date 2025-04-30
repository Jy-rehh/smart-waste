import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import RPi.GPIO as GPIO

# Set up GPIO for the first ultrasonic sensor
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

TRIG1 = 11  # GPIO Pin 11 (changed)
ECHO1 = 8   # GPIO Pin 8 (changed)

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

def send_email():
    sender_email = "smartaccesssmartwaste@gmail.com"  # Replace with your email
    receiver_email = "smartaccesssmartwaste@gmail.com"
    password = "ospk xejd cpxz djbh"  # Replace with your generated App Password

    subject = "📦 RVM Notification: Bottle Bin Full – Collection Required"
    body = """
    Hello,

    This is an automated notification from the RVM Smart Waste Smart Access System.

    The bottle bin at [Location Name] has reached full capacity as of [Date & Time]. Bottles are now ready for collection.

    Machine ID: RVM-[UniqueID]
    Location: [Location Name]
    Timestamp: [Date & Time]

    To ensure continued service and prevent overflow, please schedule a pickup at your earliest convenience.

    Thank you for your attention.

    —
    RVM System Notification
    This is a system-generated email. Please do not reply.
    """

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Secure connection
            server.login(sender_email, password)  # Login using your email and App Password
            server.sendmail(sender_email, receiver_email, msg.as_string())  # Send the email
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

try:
    while True:
        distance1 = get_distance(TRIG1, ECHO1)
        print(f"Sensor 1 Distance: {distance1} cm")

        # Logic for bottle detection
        if distance1 < 5:  # If the distance is less than 5 cm, a bottle is close
            print("Container Full!")
            send_email()  # Send email notification

        time.sleep(1)

except KeyboardInterrupt:
    print("Program stopped.")
    GPIO.cleanup()
