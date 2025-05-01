const express = require('express');
const admin = require('firebase-admin');
const path = require('path');
const { spawn } = require('child_process');
const bodyParser = require('body-parser'); 
const cors = require('cors');
const app = express();
const port = 80;

let isDetectionRunning = false;
let detectionProcess = null;
let macIpLoggerProcess = null;
let storeMacIpProcess = null;

// ✅ Initialize Firebase
const serviceAccount = require('./firebase-key.json');
admin.initializeApp({
  credential: admin.credential.cert(serviceAccount)
});

const db = admin.firestore();
app.use(express.json());
app.use(cors());
//===============================================================================
 /**
 * Start bottle session — assign queue position to a user in Users collection
 */
app.post('/start-bottle-session', async (req, res) => {
  const { mac } = req.body;
  if (!mac) return res.status(400).json({ error: 'MAC is required' });

  const usersRef = db.collection('Users Collection');
  const snapshot = await usersRef.where('queuePosition', '!=', null).orderBy('queuePosition').get();

  let nextQueuePos = 1;
  snapshot.forEach(doc => {
    const user = doc.data();
    if (user.queuePosition >= nextQueuePos) {
      nextQueuePos = user.queuePosition + 1;
    }
  });

  // Find the user by mac (userId)
  const userDoc = await usersRef.where('UserID', '==', mac).limit(1).get();
  if (userDoc.empty) {
    return res.status(404).json({ error: 'User not found' });
  }

  const docId = userDoc.docs[0].id;
  await usersRef.doc(docId).update({ queuePosition: nextQueuePos });

  res.json({ queuePosition: nextQueuePos });
});

/**
 * Finish session — remove the user from queue and shift others
 */
app.post('/finish-bottle-session', async (req, res) => {
  const { mac } = req.body;
  if (!mac) return res.status(400).json({ error: 'MAC is required' });

  const usersRef = db.collection('Users Collection');
  const userDocSnap = await usersRef.where('UserID', '==', mac).limit(1).get();

  if (userDocSnap.empty) {
    return res.status(404).json({ error: 'User not found' });
  }

  const userDoc = userDocSnap.docs[0];
  const userData = userDoc.data();
  const currentQueue = userData.queuePosition;

  if (!currentQueue) return res.status(400).json({ error: 'User is not in the queue' });

  // Remove queuePosition from current user
  await usersRef.doc(userDoc.id).update({ queuePosition: admin.firestore.FieldValue - 1 });

  // Shift queuePosition down for others
  const queueSnap = await usersRef
    .where('queuePosition', '>', currentQueue)
    .get();

  const batch = db.batch();
  queueSnap.forEach(doc => {
    const current = doc.data().queuePosition;
    batch.update(doc.ref, { queuePosition: current - 1 });
  });

  await batch.commit();
  res.json({ message: 'User removed and queue updated' });
});
/**
 * Get the MAC address of the user at queue position 1
 */
app.get('/api/get-queue-position-one', async (req, res) => {
  try {
    const usersRef = db.collection('Users Collection');
    const snapshot = await usersRef.where('queuePosition', '==', 1).limit(1).get();

    if (snapshot.empty) {
      return res.status(404).json({ error: 'No user with queuePosition 1' });
    }

    const user = snapshot.docs[0].data();
    res.json({ mac: user.UserID });
  } catch (e) {
    console.error(e);
    res.status(500).json({ error: 'Server error' });
  }
});

//===============================================================================

// Serve static files (CSS, JS, images) from the current directory
app.use(express.static(__dirname));

// Serve HTML from the templates folder
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'templates', 'index.html'));
});

// Function to start the bottle detection process
function startBottleDetection() {
  if (!isDetectionRunning) {
    const pythonExecutable = '/home/pi/smart-waste/venv/bin/python3';  // Adjust path to Python executable if needed
    //const pythonScript = '/home/pi/smart-waste/bottle_detect.py';    // Adjust path to the script if needed
    const pythonScript = '/home/pi/smart-waste/qwerty.py';

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

let startsWifiProcess = null;

function startsWifiManager() {
  if (!startsWifiProcess) {
    const pythonExecutable = '/home/pi/smart-waste/venv/bin/python3';  // Path to python executable in your virtual environment
    const pythonScript = '/home/pi/smart-waste/wifi/wifi_time_manager.py';  // Path to your Python script

    startsWifiProcess = spawn(pythonExecutable, [pythonScript]);

    // Capture stdout (output from the Python script)
    startsWifiProcess.stdout.on('data', (data) => {
      console.log(`stdout: ${data.toString()}`);  // Convert buffer data to string
    });

    // Capture stderr (errors from the Python script)
    startsWifiProcess.stderr.on('data', (data) => {
      console.error(`stderr: ${data.toString()}`);
    });

    // Handle the Python process closing
    startsWifiProcess.on('close', (code) => {
      console.log(`Child process exited with code ${code}`);
      startsWifiProcess = null;  // Reset process tracker
    });

    // Handle process errors (e.g., if the Python script crashes)
    startsWifiProcess.on('error', (err) => {
      console.error(`Failed to start Python process: ${err.message}`);
    });
  }
}
function startTestUltrasonic() {
  const pythonExecutable = '/home/pi/smart-waste/venv/bin/python3';  // Adjust if needed
  const pythonScript = '/home/pi/smart-waste/testing/test_ultrasonic.py';

  const testUltrasonicProcess = spawn(pythonExecutable, [pythonScript]);

  testUltrasonicProcess.stdout.on('data', (data) => {
    console.log(`[Ultrasonic] stdout: ${data.toString()}`);
  });

  testUltrasonicProcess.stderr.on('data', (data) => {
    console.error(`[Ultrasonic] stderr: ${data.toString()}`);
  });

  testUltrasonicProcess.on('close', (code) => {
    console.log(`[Ultrasonic] Script exited with code ${code}`);
  });
}


// Start all scripts when the server starts
function startAllScripts() {
  startBottleDetection();
  startMacIpLogger();
  startStoreMacIp();
  startsWifiManager();
  startTestUltrasonic();
}

// Start the server and run all scripts
app.listen(port, '0.0.0.0', () => {
  console.log(`Server is running at http://192.168.50.252:${port}`);
  startAllScripts();
});
