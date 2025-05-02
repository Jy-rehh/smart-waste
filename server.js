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
  const now = Date.now();
  const expirationLimit = 90 * 1000; // 90 seconds in milliseconds

  // Check if someone already has queuePosition 1
  const activeSessionSnap = await usersRef.where('queuePosition', '==', 1).limit(1).get();

  if (!activeSessionSnap.empty) {
    const activeDoc = activeSessionSnap.docs[0];
    const activeData = activeDoc.data();
    const startedAt = activeData.sessionStartedAt || 0;

    if (now - startedAt < expirationLimit) {
      if (activeData.UserID !== mac) {
        const secondsLeft = Math.ceil((expirationLimit - (now - startedAt)) / 1000);
        return res.status(403).json({
          error: 'Another user is already in session',
          secondsLeft,
        });
      }
    } else {
      // Expired — clear it
      await usersRef.doc(activeDoc.id).update({
        queuePosition: admin.firestore.FieldValue.delete(),
        sessionStartedAt: admin.firestore.FieldValue.delete(),
      });
    }
  }

  // Set current user as queuePosition 1 and save timestamp
  const userDocSnap = await usersRef.where('UserID', '==', mac).limit(1).get();
  if (userDocSnap.empty) return res.status(404).json({ error: 'User not found' });

  const docId = userDocSnap.docs[0].id;
  await usersRef.doc(docId).update({
    queuePosition: 1,
    sessionStartedAt: now,
  });

  res.json({ queuePosition: 1 });
});
/**
 * Auto delete queue
 */
exports.cleanupExpiredSessions = functions.pubsub
  .schedule('every 1 minutes')
  .onRun(async (context) => {
    const now = Date.now();
    const expirationLimit = 90 * 1000; // 90 seconds

    const usersRef = db.collection('Users Collection');
    const snapshot = await usersRef.where('queuePosition', '==', 1).get();

    if (snapshot.empty) {
      console.log('No active sessions to check.');
      return null;
    }

    for (const doc of snapshot.docs) {
      const data = doc.data();
      const startedAt = data.sessionStartedAt || 0;
      const secondsElapsed = (now - startedAt);

      if (secondsElapsed >= expirationLimit) {
        await usersRef.doc(doc.id).update({
          queuePosition: admin.firestore.FieldValue.delete(),
          sessionStartedAt: admin.firestore.FieldValue.delete(),
        });
        console.log(`Session expired and cleared for UserID: ${data.UserID}`);
      }
    }

    return null;
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

  if (userData.queuePosition !== 1) {
    return res.status(400).json({ error: 'User is not currently in session' });
  }

  // End session by removing the queuePosition
  await usersRef.doc(userDoc.id).update({ queuePosition: admin.firestore.FieldValue.delete() });

  res.json({ message: 'Session finished' });
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
    //const pythonScript = '/home/pi/smart-waste/qwerty.py';
    const pythonScript = '/home/pi/smart-waste/main.py';

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
