from flask import Flask, render_template
from flask_socketio import SocketIO
from main import generate_frames  # Import the frame generation function from main.py

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

# When the client connects, start the background task
@socketio.on('connect')
def on_connect():
    print('Client connected')
    socketio.start_background_task(generate_frames, socketio)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
