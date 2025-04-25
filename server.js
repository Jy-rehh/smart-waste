// const express = require('express');
// const path = require('path');

// const app = express();
// const port = 80;

// // Serve static files (CSS, JS, images) from smart-waste folder
// app.use(express.static(__dirname));

// // Serve HTML from the templates folder
// app.get('/', (req, res) => {
//   res.sendFile(path.join(__dirname, 'templates', 'index.html'));
// });

// app.listen(80, '0.0.0.0', () => {
//     console.log('Server is running on http://192.168.50.252:80');
// });

const express = require('express');
const path = require('path');
const app = express();
const port = 80;

let isDetectionRunning = false; // Flag to track the detection status

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
    // Example of running the Python script using subprocess
    const { spawn } = require('child_process');
    const bottleDetection = spawn('python3', ['main.py']); // Adjust this line with your actual script

    bottleDetection.stdout.on('data', (data) => {
      console.log(`stdout: ${data}`);
    });

    bottleDetection.stderr.on('data', (data) => {
      console.error(`stderr: ${data}`);
    });

    bottleDetection.on('close', (code) => {
      console.log(`child process exited with code ${code}`);
    });

    isDetectionRunning = true;
    res.json({ success: true, message: 'Detection started.' });
  } else {
    res.json({ success: false, message: 'Detection is already running.' });
  }
});

// Endpoint to stop bottle detection
app.get('/stop-detection', (req, res) => {
  if (isDetectionRunning) {
    // Logic to stop the detection (e.g., by killing the process or setting a flag)
    // Example: If using Python subprocess to control detection, you can terminate the process
    // Assuming `detectionProcess` is the reference to the process running the detection
    
    // Terminate or stop the process here, based on your logic
    // For example: detectionProcess.kill();

    isDetectionRunning = false;
    res.json({ success: true, message: 'Detection stopped.' });
  } else {
    res.json({ success: false, message: 'Detection is not running.' });
  }
});

// Start the server
app.listen(port, '0.0.0.0', () => {
  console.log(`Server is running on http://192.168.50.252:${port}`);
});
