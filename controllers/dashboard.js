import { auth, db } from "../config/firebase-config.js";
import { getDoc, doc } from "https://www.gstatic.com/firebasejs/11.4.0/firebase-firestore.js";
import { onAuthStateChanged } from "https://www.gstatic.com/firebasejs/11.4.0/firebase-auth.js";

const urlParams = new URLSearchParams(window.location.search);
const ip  = urlParams.get('ip');
const mac = urlParams.get('mac');

onAuthStateChanged(auth, async (user) => {
    if (user) {
        try {
            const userDocRef = doc(db, "Users Collection", user.uid);
            const userDocSnap = await getDoc(userDocRef);

            if (userDocSnap.exists()) {
                const userData = userDocSnap.data();
                const usernameElement = document.querySelector(".username");

                if (userData.Username) {
                    usernameElement.textContent = userData.Username;
                } else {
                    usernameElement.textContent = "No Name Found";
                }
            } else {
                console.log("No user document found!");
            }
        } catch (error) {
            console.error("Error fetching user data:", error);
        }
    } else {
        window.location.href = "/templates/login.html";
    }
});
