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

// Function to get MAC address from MikroTik given the client IP
async function getMacAddressFromIp(clientIp) {
  return new Promise((resolve, reject) => {
    const device = new MikroNode('192.168.50.1');
    device.connect('admin', '')
      .then(([login]) => {
        const chan = login.openChannel('dhcp-lease');
        chan.write('/ip/dhcp-server/lease/print');

        chan.on('done', (data) => {
          console.log('MikroTik DHCP Leases:', data);  // Log the data received from MikroTik
          const leases = MikroNode.parseItems(data);
          const matchedLease = leases.find(lease => lease.address === clientIp);

          if (matchedLease) {
            resolve(matchedLease['mac-address']);
          } else {
            resolve(null);
          }
          login.close();
        });

        chan.on('error', (err) => {
          console.error('Channel error', err);
          reject(err);
          login.close();
        });
      })
      .catch(err => {
        console.error('Connection error', err);
        reject(err);
      });
  });
}

// New route to display IP and MAC
app.get('/connected-info', async (req, res) => {
  const clientIp = req.headers['x-forwarded-for'] || req.connection.remoteAddress;

  try {
    console.log('Request received for IP:', clientIp); // Log incoming IP

    const macAddress = await getMacAddressFromIp(clientIp);

    if (macAddress) {
      console.log('MAC Address found:', macAddress); // Log the MAC address
      res.send(`
        <h1>Connected Device Info</h1>
        <p><strong>IP Address:</strong> ${clientIp}</p>
        <p><strong>MAC Address:</strong> ${macAddress}</p>
      `);
    } else {
      console.log('MAC Address not found for IP:', clientIp); // Log when no MAC address is found
      res.send(`
        <h1>Device Info Not Found</h1>
        <p><strong>IP Address:</strong> ${clientIp}</p>
        <p><strong>MAC Address:</strong> Not found in DHCP leases.</p>
      `);
    }
  } catch (error) {
    console.error('Error fetching MAC address:', error); // Log the error
    res.status(500).send('Error fetching device info.');
  }
});

const clientIp = req.headers['x-forwarded-for'] || req.connection.remoteAddress;
console.log('Client IP:', clientIp);

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
