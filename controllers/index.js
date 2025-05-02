const urlParams = new URLSearchParams(window.location.search);
const ip  = urlParams.get('ip');
const mac = urlParams.get('mac');

document.getElementById("ip-display").textContent = ip || 'Not found';
document.getElementById("mac-display").textContent = mac || 'Not found';

function hideAllModals() {
  document.getElementById("insertModal").style.display = "none";
  document.getElementById("pleaseWaitModal").style.display = "none";  
}
// Call this before doing anything else
fetch('http://192.168.50.252:80/check-and-clear-expired-session', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ mac })
})
.then(res => res.json())
.then(data => {
  console.log(data.message);
})
.catch(err => console.error("Error checking session:", err));


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
  .then(response => response.json())
  .then(data => {
    if (data.queuePosition === 1) {
      // First in line: show insert modal
      document.getElementById("insertModal").style.display = "block";
      document.getElementById("pleaseWaitModal").style.display = "none";
    } else {
      // Not first: show please wait modal with countdown
      document.getElementById("insertModal").style.display = "none";
      document.getElementById("pleaseWaitModal").style.display = "block";

      let secondsLeft = data.secondsLeft || 90;
      const countdownEl = document.getElementById("countdown");
      countdownEl.textContent = secondsLeft;

      const interval = setInterval(() => {
        secondsLeft--;
        countdownEl.textContent = secondsLeft;
        if (secondsLeft <= 0) {
          clearInterval(interval);
          location.reload(); // Retry after countdown ends
        }
      }, 1000);
    }
  })
  .catch(error => {
    console.error("Error:", error);
    // Fallback to pleaseWaitModal on error
    document.getElementById("insertModal").style.display = "none";
    document.getElementById("pleaseWaitModal").style.display = "block";

    // Optional: static fallback countdown
    let secondsLeft = 90;
    const countdownEl = document.getElementById("countdown");
    countdownEl.textContent = secondsLeft;

    const interval = setInterval(() => {
      secondsLeft--;
      countdownEl.textContent = secondsLeft;
      if (secondsLeft <= 0) {
        clearInterval(interval);
        location.reload();
      }
    }, 1000);
  });
});

function closePleaseWait() {
  document.getElementById("pleaseWaitModal").style.display = "none";
}

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

