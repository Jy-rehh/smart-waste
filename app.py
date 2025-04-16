import threading
import subprocess
import time
from flask import Flask, render_template

app = Flask(__name__)

# Function to run the bottle detection in a separate process using xvfb-run
def run_bottle_detection():
    subprocess.run(["xvfb-run", "python3", "bottle_detect.py"])

# Start the bottle detection in a separate thread
detection_thread = threading.Thread(target=run_bottle_detection, daemon=True)
detection_thread.start()

# Simple Flask web server
@app.route('/')
def index():
    return render_template("index.html")  # Assuming you have an index.html file in your templates folder

if __name__ == '__main__':
    # Run Flask app on 192.168.1.18 (accessible on local network)
    app.run(host="0.0.0.0", port=80)
