import { auth } from "../config/firebase-config.js";
import { signOut } from "https://www.gstatic.com/firebasejs/11.4.0/firebase-auth.js";

const urlParams = new URLSearchParams(window.location.search);
const ip  = urlParams.get('ip');
const mac = urlParams.get('mac');

// Logout event listener
document.querySelector(".logout-btn").addEventListener("click", () => {
    signOut(auth)
        .then(() => {
            // Clear session storage to prevent back navigation
            sessionStorage.clear();
            localStorage.clear();

            alert("Logged out successfully!");
            window.location.href = "login.html"; // Redirect to login page
        })
        .catch((error) => {
            console.error("Logout failed: ", error);
        });
});
