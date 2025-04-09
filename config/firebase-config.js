// Import Firebase modules
import { initializeApp } from "https://www.gstatic.com/firebasejs/11.4.0/firebase-app.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/11.4.0/firebase-auth.js";
import { getFirestore } from "https://www.gstatic.com/firebasejs/11.4.0/firebase-firestore.js";

// Firebase Configuration (Replace with your actual Firebase settings)
const firebaseConfig = {
    apiKey: "AIzaSyAGD9PtR-pl-Eq3Ww4m9oz7g6d8DFms0DQ",
    authDomain: "smart-waste-smart-access-a425c.firebaseapp.com",
    projectId: "smart-waste-smart-access-a425c",
    storageBucket: "smart-waste-smart-access-a425c.appspot.com",
    messagingSenderId: "162639196066",
    appId: "1:162639196066:web:5f0dc3feef24a78c520cfb"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

// Export for other scripts
export { auth, db };
