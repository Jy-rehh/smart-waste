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

// MikroTik connection details
const HOST = '192.168.50.1';  // Replace with your MikroTik IP
const USER = 'admin';         // Replace with your MikroTik username
const PASS = '';              // Replace with your MikroTik password

// Function to get the client's IP address from the request
function getClientIp(req) {
  // Try to get the IP address from headers or connection object
  return req.headers['x-forwarded-for'] || req.connection.remoteAddress || req.socket.remoteAddress || req.connection.socket.remoteAddress;
}

// Endpoint to fetch device details (IP and MAC)
app.get('/devices', async (req, res) => {
  const clientIp = getClientIp(req);  // Get the IP address of the client (requester's device)
  console.log('Client IP:', clientIp); // Debug: log the client IP to ensure it's correct

  try {
    // Connect to MikroTik using MikroNode
    const [conn, resolve] = await MikroNode.connect(HOST, USER, PASS);
    const chan = conn.openChannel('arp');
    
    // Request the ARP table from MikroTik
    const data = await chan.write('/ip/arp/print');
    const items = MikroNode.parseItems(data);

    // Find the device matching the requester's IP address in the ARP table
    const device = items.find(entry => entry.address === clientIp);
    
    if (device) {
      // If found, return the IP and MAC address of the requesting device
      res.json({
        ipAddress: device.address,
        macAddress: device['mac-address']
      });
    } else {
      // If not found, return an error message
      res.status(404).json({ error: 'Device not found in ARP table' });
    }

    // Close the connection to MikroTik
    conn.close();
  } catch (err) {
    // Handle connection errors
    console.error('Error connecting to RouterOS:', err);
    res.status(500).json({ error: 'Failed to connect to RouterOS' });
  }
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
