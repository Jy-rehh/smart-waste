let userQueue = JSON.parse(localStorage.getItem("userQueue")) || [];
let currentServingMac = localStorage.getItem("currentMac");

// Get MAC from URL (already done)
const urlParams = new URLSearchParams(window.location.search);
const userMac = urlParams.get('mac');

// Display queue
function displayQueue() {
    const queueDiv = document.createElement("div");
    queueDiv.innerHTML = `<h3>Queue:</h3><ul>${userQueue.map((mac, index) => `<li>${mac} ${index === 0 ? "(Now Serving)" : ""}</li>`).join("")}</ul>`;
    document.body.appendChild(queueDiv);
}

// Add current user to queue if not already
if (!userQueue.includes(userMac)) {
    userQueue.push(userMac);
    localStorage.setItem("userQueue", JSON.stringify(userQueue));
}

// Serve user at front of queue only
currentServingMac = userQueue[0];
localStorage.setItem("currentMac", currentServingMac);

if (userMac === currentServingMac) {
    console.log("✅ You are now connected.");
    // Here, send a request to backend to whitelist this MAC (e.g. using fetch)
    grantInternetAccess(userMac);
} else {
    console.log("⏳ Please wait. You're in the queue.");
    // Optional: disable buttons or show "Wait for your turn"
}

displayQueue();

// Simulated grant function (replace with real API call to router or server)
function grantInternetAccess(mac) {
    fetch('/grant-access', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({mac})
    }).then(res => res.json())
      .then(data => console.log("Access granted:", data))
      .catch(err => console.error(err));
}

// After bottle time is done or user clicks Done
document.getElementById("doneButton").addEventListener("click", () => {
    // Remove current user from queue
    userQueue.shift();
    localStorage.setItem("userQueue", JSON.stringify(userQueue));
    // Revoke access (via backend)
    fetch('/revoke-access', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({mac: currentServingMac})
    });
    location.reload(); // Reload page for next user
});
