import threading
import subprocess

# Function to run the bottle detection in a separate process using xvfb-run
def run_bottle_detection():
    subprocess.Popen(["xvfb-run", "python3", "bottle_detect.py"])

# Start the detection thread
thread = threading.Thread(target=run_bottle_detection, daemon=True)
thread.start()

# Keep the script alive
thread.join()
