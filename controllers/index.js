const urlParams = new URLSearchParams(window.location.search);
const ip  = urlParams.get('ip');
const mac = urlParams.get('mac');

document.getElementById("ip-display").textContent = ip || 'Not found';
document.getElementById("mac-display").textContent = mac || 'Not found';

import { initializeApp } from "https://www.gstatic.com/firebasejs/9.6.1/firebase-app.js";
import { getDatabase, ref, get } from "https://www.gstatic.com/firebasejs/9.6.1/firebase-database.js";
import { firebaseConfig } from '../config/firebase-config.js'; // relative path

const app = initializeApp(firebaseConfig);
const db = getDatabase(app);


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
  // Done button logic
  document.getElementById('doneButton').addEventListener('click', async () => {
    const mac = document.getElementById("mac-display").textContent.trim();

    if (!mac || mac === 'Not found') {
        alert("MAC address not found.");
        return;
    }

    try {
        const dbRef = ref(db, 'users');
        const snapshot = await get(dbRef);

        if (!snapshot.exists()) {
            alert("No users found.");
            return;
        }

        let foundTime = null;
        snapshot.forEach((childSnap) => {
            const val = childSnap.val();
            if (val.UserID === mac) {
                foundTime = val.WiFiTimeAvailable;
            }
        });

        if (foundTime !== null) {
            document.getElementById("time-display").innerText = `${foundTime} min`;
        } else {
            alert("No matching MAC address found.");
        }

    } catch (error) {
        console.error("Firebase fetch error:", error);
        alert(`An error occurred: ${error.message}`);
    }
});
