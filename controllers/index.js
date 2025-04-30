import { initializeApp } from "https://www.gstatic.com/firebasejs/9.22.1/firebase-app.js";
import { getDatabase, ref, get, child } from "https://www.gstatic.com/firebasejs/9.22.1/firebase-database.js";
const firebaseConfig = {
  apiKey: "AIzaSyAnY3P1JJBP6DigzoyrLw1Zikj1fH_occA",
  authDomain: "smart-waste-c39ac.firebaseapp.com",
  databaseURL: "https://smart-waste-c39ac-default-rtdb.firebaseio.com/",
  projectId: "smart-waste-c39ac",
  storageBucket: "smart-waste-c39ac.appspot.com",
  messagingSenderId: "645631527511",
  appId: "1:645631527511:web:96117a712c70e3231ef112",
  measurementId: "G-YNWWZDNHZZ"
};

const app = initializeApp(firebaseConfig);
const db = getDatabase(app);


const urlParams = new URLSearchParams(window.location.search);
const ip  = urlParams.get('ip');
const mac = urlParams.get('mac');

document.getElementById("ip-display").textContent = ip || 'Not found';
document.getElementById("mac-display").textContent = mac || 'Not found';

let displayMac = document.getElementById("mac-display").textContent;

async function fetchWifiTime(mac) {
  if (!mac || mac === 'Not found') {
    alert("MAC address is not available.");
    return;
  }

  try {
    const snapshot = await get(child(ref(db), `Users/${mac}`));
    if (snapshot.exists()) {
      const data = snapshot.val();
      const wifiTime = data.WifiTimeAvailable;

      if (typeof wifiTime === "number") {
        // Convert to hours/minutes (optional)
        const minutes = Math.floor(wifiTime / 60);
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;

        document.getElementById("wifi-time").textContent = `${hours} hr. ${mins} min.`;
      } else {
        alert("WifiTimeAvailable is not a valid number.");
      }
    } else {
      alert("User not found in Realtime Database.");
    }
  } catch (err) {
    console.error("Error fetching WifiTimeAvailable:", err);
    alert("Failed to fetch time from Firebase.");
  }
}

fetchWifiTime(displayMac);


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
    const mac = await getCurrentMacWithQueueOne();
    if (!mac) {
        alert("MAC address not found.");
        return;
    }

    // Finish the session first
    await finishSession(mac);

    // Try to fetch the time remaining
    
    try {
      
      const res = await fetch(`http://192.168.50.252:3000/api/get-time-remaining?mac=${mac}`);

        console.log("Raw response from /api/get-time-remaining:", res);

        // Check if response is ok
        if (!res.ok) {
            alert(`Server returned an error: ${res.status}`);
            return; 
        }

        // Try parsing the response JSON
        let data;
        try {
            data = await res.json();
        } catch (parseErr) {
            console.error("Failed to parse JSON:", parseErr);
            alert("Received an invalid response format.");
            return;
        }

        // Check if time_remaining exists in the response
        if (data.WifiTimeAvailable) {
          window.location.href = `index.html?time=${data.WifiTimeAvailable}&mac=${mac}`;
      } else {
          alert("Failed to get WifiTimeAvailable from server.");
      }
      
    } catch (err) {
        console.error("Error fetching time remaining:", err);
        alert("An error occurred while fetching the time remaining.");
    }
});