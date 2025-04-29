// Insert Bottles Modal
const insertModal = document.getElementById("insertModal");
const openInsertModalBtn = document.getElementById("openModal");
const closeInsertModalBtn = insertModal.querySelector(".close");
const cancelInsertBtn = insertModal.querySelector(".action-cancel");
const timerElement = document.querySelector(".my-b");
const spinner = document.querySelector(".progress-container");

const urlParams = new URLSearchParams(window.location.search);
const ip  = urlParams.get('ip');
const mac = urlParams.get('mac');

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
