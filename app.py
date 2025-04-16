import threading
from flask import Flask, render_template
import os
from bottle_detect import start_bottle_detection  # Import the function

# Initialize Flask app
app = Flask(__name__)

# Web server route to display HTML page
@app.route('/')
def home():
    return render_template('login.html')  # Ensure login.html exists in the templates folder

# Run web server in a separate thread
def run_flask_app():
    app.run(host='0.0.0.0', port=80)

# Start the Flask server thread
flask_thread = threading.Thread(target=run_flask_app)
flask_thread.daemon = True
flask_thread.start()

# Start the bottle detection in a separate thread
bottle_detection_thread = threading.Thread(target=start_bottle_detection, daemon=True)
bottle_detection_thread.start()

# Run the main loop or additional logic if needed
try:
    while True:
        # Keep the main thread alive while Flask server and bottle detection are running
        pass

except KeyboardInterrupt:
    print("🛑 Exiting gracefully...")
