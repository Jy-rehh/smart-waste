const express = require('express');
const path = require('path');
const { spawn } = require('child_process');
const app = express();
const port = 80;

let isDetectionRunning = false;
let detectionProcess = null;

// Serve static files (CSS, JS, images) from the same directory
app.use(express.static(__dirname));

// Serve the main page
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'templates', 'index.html'));
});

// Start detection
app.get('/start-detection', (req, res) => {
  if (isDetectionRunning) {
    return res.json({ success: false, message: 'Detection already running.' });
  }

  const pythonExecutable = '/home/pi/smart-waste/venv/bin/python3';  
  const pythonScript = '/home/pi/smart-waste/bottle_detect.py';

  detectionProcess = spawn(pythonExecutable, [pythonScript]);

  detectionProcess.stdout.on('data', (data) => {
    console.log(`stdout: ${data}`);
  });

  detectionProcess.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
  });

  detectionProcess.on('close', (code) => {
    console.log(`Python process exited with code ${code}`);
    isDetectionRunning = false;
    detectionProcess = null;
  });

  isDetectionRunning = true;
  res.json({ success: true, message: 'Detection started.' });
});

// Stop detection
app.get('/stop-detection', (req, res) => {
  if (!isDetectionRunning || !detectionProcess) {
    return res.json({ success: false, message: 'Detection not running.' });
  }

  detectionProcess.kill('SIGTERM');

  detectionProcess.on('close', (code) => {
    console.log(`Python process terminated with code ${code}`);
  });

  isDetectionRunning = false;
  detectionProcess = null;

  res.json({ success: true, message: 'Detection stopped.' });
});

// Start server
app.listen(port, '0.0.0.0', () => {
  console.log(`Server is running at http://192.168.50.252:${port}`);
});
