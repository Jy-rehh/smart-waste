const urlParams = new URLSearchParams(window.location.search);
const ip  = urlParams.get('ip');
const mac = urlParams.get('mac');

document.getElementById("ip-display").textContent = ip || 'Not found';
document.getElementById("mac-display").textContent = mac || 'Not found';

document.getElementById("openModal").addEventListener("click", function () {
    if (!mac || !ip) {
        alert("MAC or IP not found in URL.");
        return;
    }

    fetch('http://192.168.50.252:80/start-bottle-session', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            mac: mac,
            ip: ip
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log("[✔] Session started:", data);
        // Optionally show a modal or status
    })
    .catch(error => {
        console.error("[!] Error starting session:", error);
    });
});
async function getCurrentMacWithQueueOne() {
    try {
      const response = await fetch('/api/get-queue-position-one'); // see backend for this
      const data = await response.json();
      return data.mac;
    } catch (err) {
      console.error("Error fetching current MAC:", err);
    }
  }

  async function finishSession(mac) {
    try {
      const res = await fetch('/finish-bottle-session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ mac })
      });

      const data = await res.json();
      if (res.ok) {
        alert("Session ended, queue updated!");
        // Optionally reload or update UI
      } else {
        alert(`Error: ${data.error}`);
      }
    } catch (err) {
      console.error("Failed to finish session:", err);
    }
  }

  document.getElementById('cancelButton').addEventListener('click', async () => {
    const mac = await getCurrentMacWithQueueOne();
    if (mac) {
      await finishSession(mac);
    }
  });

  document.getElementById('doneButton').addEventListener('click', async () => {
    const mac = await getCurrentMacWithQueueOne();
    if (mac) {
      await finishSession(mac);
    }
  });

  
  const firebaseConfig = require('../firebase-key.json');
  admin.initializeApp({
    credential: admin.credential.cert(firebaseConfig)
  });

// Initialize Firebase
firebase.initializeApp(firebaseConfig);
const db = firebase.database();

// Load time from Firebase based on MAC address
async function loadWiFiTime(mac) {
  try {
    const snapshot = await db.ref(`users/${mac}/WiFiTimeAvailable`).once('value');
    const timeInSeconds = snapshot.val();

    if (typeof timeInSeconds === 'number') {
      const hrs = Math.floor(timeInSeconds / 3600);
      const mins = Math.floor((timeInSeconds % 3600) / 60);
      const secs = timeInSeconds % 60;
      document.getElementById('wifi-time').textContent = `${hrs} hr. ${mins} min. ${secs} sec.`;
    } else {
      document.getElementById('wifi-time').textContent = "No time available.";
    }
  } catch (err) {
    console.error("Failed to load WiFi time:", err);
    document.getElementById('wifi-time').textContent = "Error loading time.";
  }
}

// Wait for the page to load, then fetch time
window.addEventListener("DOMContentLoaded", () => {
  if (mac) {
    loadWiFiTime(mac);
  }
});