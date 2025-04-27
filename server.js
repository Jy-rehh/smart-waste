const express = require('express');
const path = require('path');
const { spawn } = require('child_process');
const app = express();
const port = 80;
const firebaseAdmin = require('firebase-admin');
const { exec } = require('child_process');

// Initialize Firebase Admin SDK
firebaseAdmin.initializeApp({
  credential: firebaseAdmin.credential.cert('firebase-key.json'),
});
const db = firebaseAdmin.firestore();

// MikroTik Router API details (replace with actual credentials)
const { connect } = require('librouteros');
const api = connect({
  username: 'admin',
  password: '',
  host: '192.168.50.1',
});

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

// Function to revert the user's access to "regular" in MikroTik router
async function revertToRegular(macAddress) {
  try {
    const bindings = await api.path('ip', 'hotspot', 'ip-binding').get();
    const binding = bindings.find(b => b['mac-address'].toLowerCase() === macAddress.toLowerCase());

    if (binding) {
      console.log(`[*] Found binding for ${macAddress}, reverting to regular access...`);
      await api.path('ip', 'hotspot', 'ip-binding').set({
        '.id': binding['.id'],
        'type': 'regular',  // Reverts to regular access
      });
      console.log(`[*] Successfully reverted ${macAddress} to regular access.`);
    } else {
      console.log(`[!] No binding found for MAC: ${macAddress}`);
    }
  } catch (error) {
    console.error('[!] Error during revert:', error);
  }
}

// Function to check and update Wi-Fi time for users
async function checkUserTime() {
  try {
    const usersSnapshot = await db.collection('Users Collection').get();

    usersSnapshot.forEach(async (userDoc) => {
      const userData = userDoc.data();
      const macAddress = userData.MACAddress;  // Assuming MACAddress is stored in Firestore
      const wifiTimeAvailable = userData.WiFiTimeAvailable;

      if (wifiTimeAvailable <= 0) {
        // If WiFi time is zero or negative, revert the access to regular
        console.log(`[*] User ${macAddress} time expired, reverting access.`);
        await revertToRegular(macAddress);
      }
    });
  } catch (error) {
    console.error('[!] Error while checking user WiFi time:', error);
  }
}

// Set an interval to check the user time every minute (adjust as needed)
setInterval(checkUserTime, 60 * 1000);  // 1 minute interval

// Start the server
app.listen(port, '0.0.0.0', () => {
  console.log(`Server is running on http://192.168.50.252:${port}`);
});
