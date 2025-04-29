import { auth, db } from "../config/firebase-config.js";
import { signInWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/11.4.0/firebase-auth.js";
import { collection, query, where, getDocs } from "https://www.gstatic.com/firebasejs/11.4.0/firebase-firestore.js";

const urlParams = new URLSearchParams(window.location.search);
const ip  = urlParams.get('ip');
const mac = urlParams.get('mac');

document.getElementById("login-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    const usernameInput = document.getElementById("username").value.trim();
    const passwordInput = document.getElementById("password").value.trim();

    try {
        // Search by field "Username" (with capital U)
        const usersRef = collection(db, "Users Collection");
        const q = query(usersRef, where("Username", "==", usernameInput));
        const querySnapshot = await getDocs(q);

        if (querySnapshot.empty) {
            alert("Username not found.");
            return;
        }

        const userDoc = querySnapshot.docs[0];
        const userData = userDoc.data();
        const userEmail = userData.Email; // capital E for Email field

        // Now sign in with email and password
        const userCredential = await signInWithEmailAndPassword(auth, userEmail, passwordInput);
        const user = userCredential.user;
        console.log("Login successful:", user.uid);

        alert("Login successful! Redirecting...");
        window.location.href = "dashboard.html";

    } catch (error) {
        console.error("Login failed:", error.message);
        alert("Login failed: " + error.message);
    }
});
