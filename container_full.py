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

# Function to get distance from ultrasonic sensor
def get_distance(TRIG, ECHO):
    GPIO.output(TRIG, GPIO.LOW)
    time.sleep(0.5)
    GPIO.output(TRIG, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIG, GPIO.LOW)

    while GPIO.input(ECHO) == GPIO.LOW:
        pulse_start = time.time()

    while GPIO.input(ECHO) == GPIO.HIGH:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)

    return distance

# Function to send email
def send_email():
    sender_email = "smartwastesmartaccess@gmail.com"
    receiver_email = "smartwastesmartaccess@gmail.com"
    password = "swsa123456"  # Sender's email password

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

    # Set up MIME structure
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to Gmail SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Start TLS for security
        server.login(sender_email, password)  # Login with your Gmail account
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)  # Send email
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error: {e}")

# Main loop to monitor ultrasonic sensor and send email when container is full
try:
    while True:
        distance1 = get_distance(TRIG1, ECHO1)
        print(f"Sensor 1 Distance: {distance1} cm")

        # Logic for bottle detection
        if distance1 < 5:  # If the distance is less than 5 cm, a bottle is close
            print("Container Full!")
            send_email()  # Send email when container is full

        time.sleep(1)

except KeyboardInterrupt:
    print("Program stopped.")
    GPIO.cleanup()
