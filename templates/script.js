// Insert Bottles Modal
const insertModal = document.getElementById("insertModal");
const openInsertModalBtn = document.getElementById("openModal");
const closeInsertModalBtn = insertModal.querySelector(".close");
const cancelInsertBtn = insertModal.querySelector(".action-cancel");
const doneInsertBtn = insertModal.querySelector(".action-done");
const timerElement = document.querySelector(".my-b");
const spinner = document.querySelector(".progress-container");

let countdown; // Declare countdown globally

// Open Insert Bottles Modal
openInsertModalBtn.addEventListener("click", () => {
    insertModal.style.display = "flex";
    
    // Reset & Show Loading Bar
    progressBar.style.width = "100%"; 
    timerElement.textContent = "90 sec"; 

    clearInterval(countdown); // Reset previous timer
    startCountdown(90); // Start new timer
});

// Close Insert Bottles Modal
function closeInsertModal() {
    insertModal.style.display = "none";
    clearInterval(countdown); // Stop timer when closing manually
}

closeInsertModalBtn.addEventListener("click", closeInsertModal);
cancelInsertBtn.addEventListener("click", closeInsertModal);

// Close Insert Bottles Modal when clicking outside
window.addEventListener("click", (e) => {
    if (e.target === insertModal) {
        closeInsertModal();
    }
});

// Timer function
function startCountdown(durationInSeconds) {
    let timeLeft = durationInSeconds;
    timerElement.textContent = `${timeLeft} sec`;

    const progressBar = document.getElementById("progressBar");
    progressBar.style.width = "100%"; // Start full

    countdown = setInterval(() => {
        timeLeft--;
        timerElement.textContent = `${timeLeft} sec`;

        let progress = (timeLeft / durationInSeconds) * 100;
        progressBar.style.width = progress + "%"; // Decrease bar width

        if (timeLeft <= 0) {
            clearInterval(countdown);
            timerElement.textContent = "Time's up!";
            progressBar.style.width = "0%"; // Empty the bar

            setTimeout(() => {
                insertModal.style.display = "none"; // Auto close modal
            }, 1000);
        }
    }, 1000);
}

// Fetch time_remaining from Firestore and redirect to index.html
async function fetchTimeRemainingAndRedirect(mac) {
    try {
        const res = await fetch(`/api/get-time-remaining?mac=${mac}`);
        const data = await res.json();

        if (res.ok && data.time_remaining) {
            // Redirect to index.html with time_remaining in URL
            window.location.href = `index.html?time=${data.time_remaining}&mac=${mac}`;
        } else {
            alert("Failed to get time remaining.");
        }
    } catch (err) {
        console.error("Error fetching time remaining:", err);
        alert("An error occurred while fetching the time remaining.");
    }
}

// Handle cancel button click
cancelInsertBtn.addEventListener("click", () => {
    insertModal.style.display = "none"; // Close modal on cancel
    clearInterval(countdown); // Stop the countdown
});

// Handle done button click
doneInsertBtn.addEventListener("click", async () => {
    const mac = "AA:BB:CC:DD:EE:FF"; // Replace with actual MAC address (e.g., from URL params or elsewhere)
    
    // Fetch time remaining and redirect to index.html
    await fetchTimeRemainingAndRedirect(mac);
});


// Wi-Fi Rates Modal
const ratesModal = document.getElementById("ratesModal");
const openRatesBtn = document.getElementById("openRatesModal");
const closeRatesBtn = ratesModal.querySelector(".close-btn");

// Open Wi-Fi Rates Modal
openRatesBtn.addEventListener("click", () => {
    ratesModal.style.display = "flex";
});

// Close Wi-Fi Rates Modal
closeRatesBtn.addEventListener("click", () => {
    ratesModal.style.display = "none";
});

// Close Wi-Fi Rates Modal when clicking outside
window.addEventListener("click", (e) => {
    if (e.target === ratesModal) {
        ratesModal.style.display = "none";
    }
});
