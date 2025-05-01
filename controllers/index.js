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
}); 

function closePleaseWait() {
  document.getElementById("pleaseWaitModal").style.display = "none";
}

document.getElementById("openModal").addEventListener("click", () => {
  const mac = new URLSearchParams(window.location.search).get('mac');
  const ip = new URLSearchParams(window.location.search).get('ip');

  if (!mac || !ip) {
      alert("MAC or IP is missing from URL.");
      return;
  }

  fetch('http://192.168.50.252:80/start-bottle-session', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
      },
      body: JSON.stringify({ mac }),
  })
  .then(response => response.json())
  .then(data => {
      if (data.queuePosition === 1) {
          console.log("✅ You're first in queue. Start inserting bottles.");
          // Continue with bottle detection or other logic
      } else {
          console.log("⛔ Please wait. Showing modal.");
          document.getElementById("pleaseWaitModal").style.display = "block";
      }
  })
  .catch(error => {
      console.error("[!] Error:", error);
  });
});
