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
    
    
    try {
        const mac = urlParams.get('mac'); // Replace with actual MAC address (e.g., from URL params or elsewhere)

        const res = await fetch(`/api/get-wifi-time-available?mac=${mac}`); // Adjust this API endpoint accordingly
        const data = await res.json();

        if (res.ok && data.wifi_time_available) {
            // Display WiFi Time Available in the HTML
            const wifiTimeElement = document.getElementById('wifi-time');
            wifiTimeElement.textContent = `${data.wifi_time_available.hr} hr. ${data.wifi_time_available.min} min. ${data.wifi_time_available.sec} sec`;

            // 🔁 Optionally redirect to index.html with time_remaining and mac in URL if needed
            window.location.href = `templates/index.html?time=${data.time_remaining}&mac=${mac}`;
        } else {
            alert("Failed to get WiFi Time Available.");
        }
    } catch (err) {
        console.error("Error fetching WiFi time available:", err);
        alert("An error occurred while fetching the WiFi time available.");
    }
});

// Function to check the network status
function checkNetwork(event, url) {
    if (navigator.onLine) {
        // If online, allow the link to function as usual
        window.location.href = url;
    } else {
        // If offline, prevent the link click and show an alert
        event.preventDefault();
        alert("You are offline. Please connect to the internet to proceed.");
    }
}

// Call checkNetwork when trying to navigate
document.getElementById('doneButton').addEventListener('click', function(event) {
    checkNetwork(event, 'index.html'); // Replace 'index.html' with your desired URL
});

// Prevent page from closing if offline
window.onbeforeunload = function(event) {
    if (!navigator.onLine) {
        return "You are offline. Are you sure you want to leave?";
    }
};