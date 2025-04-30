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
  // Done button logic
  document.getElementById('doneButton').addEventListener('click', async () => {
    const mac = document.getElementById("mac-display").textContent.trim();

    if (!mac || mac === 'Not found') {
        alert("MAC address not found.");
        return;
    }

    // Finish the session (your existing logic)
    await finishSession(mac);

    try {
        // Reference Firebase Realtime DB
        const dbRef = firebase.database().ref('users'); // Adjust the path as needed

        // Fetch all users once
        const snapshot = await dbRef.once('value');

        if (!snapshot.exists()) {
            alert("No users found in database.");
            return;
        }

        let matchedUser = null;

        snapshot.forEach(childSnapshot => {
            const userData = childSnapshot.val();

            if (userData.UserID === mac) {
                matchedUser = userData;
            }
        });

        if (!matchedUser) {
            alert("No user found matching the MAC address.");
            return;
        }

        const timeRemaining = matchedUser.WiFiTimeAvailable;

        if (typeof timeRemaining !== 'undefined') {
          document.getElementById("time-display").innerText = `${timeRemaining} min`;
          window.location.href = `index.html?time=${timeRemaining}&mac=${mac}`;
        } else {
            alert("WiFiTimeAvailable not found for this user.");
        }

    } catch (err) {
        console.error("Error fetching time from Firebase:", err);
        alert("An error occurred while fetching time from the database.");
    }
});
