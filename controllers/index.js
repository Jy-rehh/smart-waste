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
      body: JSON.stringify({ mac, ip })
  })
  .then(response => {
      if (!response.ok) {
          return response.json().then(data => {
              throw new Error(data.error || 'Failed to start session');
          });
      }
      return response.json();
  })
  .then(data => {
      console.log("[✔] Session started:", data);
      const modal = document.getElementById("insertModal");
      if (modal) modal.style.display = "block";
  })
  .catch(error => {
      console.error("[!] Error starting session:", error);

      // Show pleaseWaitModal if another user is already in session
      if (error.message === "Another user is already in session") {
          const pleaseWaitModal = document.getElementById("pleaseWaitModal");
          if (pleaseWaitModal) pleaseWaitModal.style.display = "block";
      } else {
          alert(`Error: ${error.message}`);
      }
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

document.getElementById("doneButton").addEventListener("click", function () {
  const modal = document.getElementById("insertModal");
  if (modal) {
      modal.style.display = "none";
  }
});
function closePleaseWait() {
  const modal = document.getElementById("pleaseWaitModal");
  if (modal) modal.style.display = "none";
}
