const urlParams = new URLSearchParams(window.location.search);
const ip  = urlParams.get('ip');
const mac = urlParams.get('mac');

      // Firebase Firestore initialization
import { initializeApp } from "https://www.gstatic.com/firebasejs/9.22.1/firebase-app.js";
import { getFirestore, doc, getDoc } from "https://www.gstatic.com/firebasejs/9.22.1/firebase-firestore.js";

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
  // Done button logic
  /*document.getElementById('doneButton').addEventListener('click', async () => {
    const mac = await getCurrentMacWithQueueOne();
    if (!mac) {
        alert("MAC address not found.");
        return;
    }

    // Finish the session first
    await finishSession(mac);

    // Try to fetch the time remaining
    
    try {
        const res = await fetch(`/api/get-time-remaining?mac=${mac}`);
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
        if (data.time_remaining) {
            window.location.href = `index.html?time=${data.time_remaining}&mac=${mac}`;
        } else {
            alert("Failed to get time remaining from server.");
        }

    } catch (err) {
        console.error("Error fetching time remaining:", err);
        alert("An error occurred while fetching the time remaining.");
    }
}); */
  
document.getElementById('doneButton').addEventListener('click', async () => {
  const mac = await getCurrentMacWithQueueOne();
  if (!mac) {
      alert("MAC address not found.");
      return;
  }

  // Finish the session first
  await finishSession(mac);

  // Fetch the remaining time from Firestore
    try {
        const firebaseConfig = {
          apiKey: "AIzaSyAnY3P1JJBP6DigzoyrLw1Zikj1fH_occA",
          authDomain: "smart-waste-c39ac.firebaseapp.com",
          projectId: "smart-waste-c39ac",
          databaseURL: "https://smart-waste-c39ac-default-rtdb.firebaseio.com/",
          storageBucket: "smart-waste-c39ac.firebasestorage.app",
          messagingSenderId: "645631527511",
          appId: "1:645631527511:web:96117a712c70e3231ef112",
          measurementId: "G-YNWWZDNHZZ"
        };

        const app = initializeApp(firebaseConfig);
        const db = getFirestore(app);

        // Fetch the user's document from Firestore
        const docRef = doc(db, "Users", mac);
        const docSnap = await getDoc(docRef);

        if (docSnap.exists()) {
            const data = docSnap.data();
            const timeRemaining = data.time_remaining;

            // Check if time_remaining exists and is a valid number
            if (typeof timeRemaining === 'number') {
                // Optional: Convert seconds to HH:MM:SS format
                const minutes = Math.floor(timeRemaining / 60);
                const hours = Math.floor(minutes / 60);
                const mins = minutes % 60;

                // Update the UI
                document.getElementById("wifi-time").innerText = `${hours} hr. ${mins} min.`;
                document.getElementById("mac-display").innerText = mac;

                // Redirect to index.html with time and mac in the query string
                window.location.href = `index.html?time=${timeRemaining}&mac=${mac}`;
              } else {
                alert("Invalid time_remaining value.");
            }
        } else {
            alert("User not found in Firestore.");
        }

    } catch (err) {
        console.error("Error fetching data from Firestore:", err);
        alert("An error occurred while fetching the time remaining.");
    }
}); 