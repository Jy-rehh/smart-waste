const express = require('express');
const admin = require('firebase-admin');
const path = require('path');
const MikroNode = require('mikronode-ng');
const MikroNode = require('mikronode');
const { spawn } = require('child_process');
const cors = require('cors');
const app = express();
const port = 80;

let isDetectionRunning = false;
let detectionProcess = null;
let macIpLoggerProcess = null;
let storeMacIpProcess = null;

// ===================================================================
// Function to get MAC address from MikroTik for a specific IP
async function getMacAddressFromIp(clientIp) {
    return new Promise((resolve, reject) => {
        const device = new MikroNode('192.168.50.1'); // Replace with your MikroTik IP

        device.connect('admin', '') // Replace with your MikroTik username/password
            .then(([login]) => {
                const chan = login.openChannel('leases');
                chan.write('/ip/dhcp-server/lease/print');

                chan.on('done', (data) => {
                    const leases = MikroNode.parseItems(data);
                    const match = leases.find(lease => lease.address === clientIp);
                    login.close();
                    if (match) {
                        resolve(match['mac-address']);
                    } else {
                        resolve(null);
                    }
                });

                chan.on('error', (err) => {
                    login.close();
                    reject(err);
                });
            })
            .catch((err) => {
                reject(err);
            });
    });
}

// ===============================================================
// Route to show current user's IP and MAC only
app.get('/connected-info', async (req, res) => {
    const clientIp = req.headers['x-forwarded-for'] || req.connection.remoteAddress;

    // Remove "::ffff:" from IPv4-mapped IPv6 address
    const cleanedIp = clientIp.replace('::ffff:', '');

    try {
        const macAddress = await getMacAddressFromIp(cleanedIp);

        if (macAddress) {
            res.send(`
                <h1>Device Info</h1>
                <p><strong>IP:</strong> ${cleanedIp}</p>
                <p><strong>MAC:</strong> ${macAddress}</p>
            `);
        } else {
            res.send(`
                <h1>Device Info</h1>
                <p><strong>IP:</strong> ${cleanedIp}</p>
                <p><strong>MAC:</strong> Not found in MikroTik DHCP leases</p>
            `);
        }
    } catch (error) {
        console.error(error);
        res.status(500).send('Error fetching MAC address from MikroTik');
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
