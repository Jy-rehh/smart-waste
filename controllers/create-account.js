// Import Firebase services from firebase-config.js
import { auth, db } from "../config/firebase-config.js";
import { createUserWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/11.4.0/firebase-auth.js";
import { doc, setDoc } from "https://www.gstatic.com/firebasejs/11.4.0/firebase-firestore.js";

const urlParams = new URLSearchParams(window.location.search);
const ip  = urlParams.get('ip');
const mac = urlParams.get('mac');

// Wait until the DOM is fully loaded
document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("create-account-btn").addEventListener("click", async () => {
        const username = document.getElementById("username").value;
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;
        const verifyPassword = document.getElementById("verify-password").value;

        if (password !== verifyPassword) {
            alert("Passwords do not match!");
            return;
        }

        try {
            // Create user in Firebase Auth (Firebase securely hashes the password)
            const userCredential = await createUserWithEmailAndPassword(auth, email, password);
            const user = userCredential.user;
            console.log("User created:", user.uid);

            // Store user data in Firestore (without password)
            await setDoc(doc(db, "Users Collection", user.uid), {
                UserID: user.uid,
                Username: username,
                Email: email,
                LoyaltyPoints: 0.0,
                RewardPoints: 0.0,
                TotalBottlesDeposited: 0,
                WiFiTimeAvailable: 0.0
            });

            alert("Account created successfully!");
            window.location.href = "login.html"; // Redirect to login page
        } catch (error) {
            console.error("Error creating account:", error);
            alert("Error: " + error.message);
        }
    });
    document.getElementById("cancel-btn").addEventListener("click", async () =>{
         window.location.href = "login.html";
    });
});
