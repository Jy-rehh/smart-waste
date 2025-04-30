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
});
  