// Insert Bottles Modal
const insertModal = document.getElementById("insertModal");
const openInsertModalBtn = document.getElementById("openModal");
const closeInsertModalBtn = insertModal.querySelector(".close");
const cancelInsertBtn = insertModal.querySelector(".action-cancel");
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

// System activation
let stopProcessTimeout = null;

function startBottleDetection() {
    fetch("/start-detection", { method: "GET" })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log("Detection started.");
                
                // Set a timeout to stop the process after 1m 30s (90 seconds)
                stopProcessTimeout = setTimeout(stopBottleDetection, 90 * 1000);
            }
        })
        .catch(error => console.error("Error starting detection:", error));
}

function stopBottleDetection() {
    fetch("/stop-detection", { method: "GET" })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log("Detection stopped.");
            }
        })
        .catch(error => console.error("Error stopping detection:", error));
}

// Event listener for the "Insert Bottles" button
document.getElementById("openModal").addEventListener("click", startBottleDetection);

// Event listener for the "Cancel" button
document.querySelector(".action-cancel").addEventListener("click", () => {
    console.log("Cancel button clicked.");
    clearTimeout(stopProcessTimeout);  // Clear the auto-stop timer
    stopBottleDetection();
});

// Event listener for the "Done" button
document.querySelector(".action-done").addEventListener("click", () => {
    console.log("Done button clicked.");
    clearTimeout(stopProcessTimeout);  // Clear the auto-stop timer
    stopBottleDetection();
});

