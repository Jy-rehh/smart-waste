import { auth, db } from "../config/firebase-config.js";
import { signInWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/11.4.0/firebase-auth.js";
import { doc, getDoc } from "https://www.gstatic.com/firebasejs/11.4.0/firebase-firestore.js";

document.getElementById("login-form").addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try {
        const userCredential = await signInWithEmailAndPassword(auth, email, password);
        const user = userCredential.user;
        console.log("Login successful:", user.uid);

        // Fetch user details from Firestore
        const userRef = doc(db, "Users Collection", user.uid);
        const userSnap = await getDoc(userRef);

        if (userSnap.exists()) {
            console.log("User data:", userSnap.data());
            alert("Login successful! Redirecting...");
            window.location.href = "dashboard.html";
        } else {
            console.error("No such user found in Firestore!");
            alert("User not found in database.");
        }
    } catch (error) {
        console.error("Login failed:", error.message);
        alert("Login failed: " + error.message);
    }
});
