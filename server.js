const express = require('express');
const path = require('path');
const { spawn } = require('child_process');
const RouterOS = require('node-routeros');  // Importing the module correctly
const app = express();
const port = 80;

let isDetectionRunning = false; // Flag to track the detection status
let detectionProcess = null;    // Variable to store the running Python process

// Serve static files (CSS, JS, images) from the smart-waste folder
app.use(express.static(__dirname));

// Serve HTML from the templates folder
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'templates', 'index.html'));
});

// Endpoint to start bottle detection
app.get('/start-detection', (req, res) => {
  if (!isDetectionRunning) {
    // Start bottle detection in the backend (e.g., using subprocess or another method)
    const pythonExecutable = '/home/pi/smart-waste/venv/bin/python3';  // Adjust if needed
    const pythonScript = '/home/pi/smart-waste/main.py';  // Adjust if needed

    detectionProcess = spawn(pythonExecutable, [pythonScript]);

    detectionProcess.stdout.on('data', (data) => {
        console.log(`stdout: ${data}`);
    });

    detectionProcess.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`);
    });

    detectionProcess.on('close', (code) => {
        console.log(`Python process exited with code ${code}`);
        isDetectionRunning = false; // Set the flag to false when the process ends
    });

    isDetectionRunning = true;
    res.json({ success: true, message: 'Detection started.' });
  } else {
    res.json({ success: false, message: 'Detection is already running.' });
  }
});

// Endpoint to stop bottle detection
app.get('/stop-detection', (req, res) => {
  if (isDetectionRunning && detectionProcess) {
    // Stop the Python process (detection) by calling .kill() on the subprocess
    detectionProcess.kill('SIGTERM');  // This sends a termination signal to the process

    detectionProcess.on('close', (code) => {
        console.log(`Python process terminated with code ${code}`);
    });

    isDetectionRunning = false; // Update the detection status
    res.json({ success: true, message: 'Detection stopped.' });
  } else {
    res.json({ success: false, message: 'Detection is not running.' });
  }
});

// Connect to RouterOS and check some basic data
const conn = RouterOS({  // Initialize RouterOS connection properly
  host: '192.168.50.1',  // Replace with your router's IP address
  user: 'admin',      // Replace with your RouterOS username
  pass: '',   // Replace with your RouterOS password
});

conn.connect()
  .then(() => {
    console.log('Connected to RouterOS');
    return conn.write('/interface/print'); // Example: Get a list of interfaces
  })
  .then((result) => {
    console.log('RouterOS Interface Info:', result);
  })
  .catch((err) => {
    console.error('Error connecting to RouterOS:', err);
  });

// Start the server
app.listen(port, '0.0.0.0', () => {
  console.log(`Server is running on http://192.168.50.252:${port}`);
});
