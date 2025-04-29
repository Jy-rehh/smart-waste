const express = require('express');
const admin = require('firebase-admin');
const path = require('path');
const MikroNode = require('mikronode-ng');
const { spawn } = require('child_process');
const cors = require('cors');
const app = express();
const port = 80;

let isDetectionRunning = false;
let detectionProcess = null;
let macIpLoggerProcess = null;
let storeMacIpProcess = null;

//==========================================================================
app.use(cors());

// Function to get the client's MAC address
// For demonstration, assuming MAC is passed as query parameter
app.get('/devices', (req, res) => {
    const macAddress = req.query.mac;  // Get MAC address from query

    if (!macAddress) {
        return res.status(400).json({ error: 'MAC address is required' });
    }

    // Adjust paths for the Python executable and script
    const pythonExecutable = '/home/pi/smart-waste/venv/bin/python3';  // Path to Python executable in the virtual environment
    const pythonScript = '/home/pi/smart-waste/routeros_get_device.py';  // Path to your Python script

    // Run the Python script to fetch device info based on MAC address
    exec(`${pythonExecutable} ${pythonScript} ${macAddress}`, (error, stdout, stderr) => {
        if (error) {
            console.error(`Error executing Python script: ${error}`);
            return res.status(500).json({ error: 'Error connecting to RouterOS' });
        }
        if (stderr) {
            console.error(`stderr: ${stderr}`);
            return res.status(500).json({ error: 'Error in Python script' });
        }

        // Parse and send the response from the Python script
        try {
            const deviceInfo = JSON.parse(stdout);
            res.json(deviceInfo);
        } catch (err) {
            console.error('Error parsing Python script output:', err);
            res.status(500).json({ error: 'Failed to parse device information' });
        }
    });
});

// ==================================================================

// Serve static files (CSS, JS, images) from the current directory
app.use(express.static(__dirname));

// Serve HTML from the templates folder
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'templates', 'index.html'));
});

// Endpoint to stop bottle detection
app.get('/stop-detection', (req, res) => {
  if (isDetectionRunning && detectionProcess) {
    // Stop the Python process (detection)
    detectionProcess.kill('SIGTERM'); // Sends a termination signal to the process

    detectionProcess.on('close', (code) => {
      console.log(`Python process terminated with code ${code}`);
    });

    isDetectionRunning = false; // Update the detection status
    detectionProcess = null;
    res.json({ success: true, message: 'Detection stopped.' });
  } else {
    res.json({ success: false, message: 'Detection is not running.' });
  }
});

// Function to start the bottle detection process
function startBottleDetection() {
  if (!isDetectionRunning) {
    const pythonExecutable = '/home/pi/smart-waste/venv/bin/python3';  // Adjust path to Python executable if needed
    const pythonScript = '/home/pi/smart-waste/bottle_detect.py';    // Adjust path to the script if needed

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
    console.log("Bottle detection started automatically.");
  }
}

// Function to start the mac_ip_logger.py script
function startMacIpLogger() {
  if (!macIpLoggerProcess) {
    const pythonExecutable = '/home/pi/smart-waste/venv/bin/python3';  // Adjust if needed
    const pythonScript = '/home/pi/smart-waste/mac_ip_logger.py';   // Adjust if needed

    macIpLoggerProcess = spawn(pythonExecutable, [pythonScript]);

    macIpLoggerProcess.stdout.on('data', (data) => {
      console.log(`stdout: ${data}`);
    });

    macIpLoggerProcess.stderr.on('data', (data) => {
      console.error(`stderr: ${data}`);
    });

    macIpLoggerProcess.on('close', (code) => {
      console.log(`mac_ip_logger.py exited with code ${code}`);
      macIpLoggerProcess = null;
    });

    console.log("MAC IP Logger started.");
  }
}

// Function to start the store_mac_ip.py script
function startStoreMacIp() {
  if (!storeMacIpProcess) {
    const pythonExecutable = '/home/pi/smart-waste/venv/bin/python3';  // Adjust if needed
    const pythonScript = '/home/pi/smart-waste/store_mac_ip.py';    // Adjust if needed

    storeMacIpProcess = spawn(pythonExecutable, [pythonScript]);

    storeMacIpProcess.stdout.on('data', (data) => {
      console.log(`stdout: ${data}`);
    });

    storeMacIpProcess.stderr.on('data', (data) => {
      console.error(`stderr: ${data}`);
    });

    storeMacIpProcess.on('close', (code) => {
      console.log(`store_mac_ip.py exited with code ${code}`);
      storeMacIpProcess = null;
    });

    console.log("Store MAC IP script started.");
  }
}

// Start all scripts when the server starts
function startAllScripts() {
  startBottleDetection();
  startMacIpLogger();
  startStoreMacIp();
}

// Start the server and run all scripts
app.listen(port, '0.0.0.0', () => {
  console.log(`Server is running at http://192.168.50.252:${port}`);
  startAllScripts();
});
