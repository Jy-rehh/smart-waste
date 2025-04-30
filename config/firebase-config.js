// // Import Firebase modules
// import { initializeApp } from "https://www.gstatic.com/firebasejs/11.4.0/firebase-app.js";
// import { getAuth } from "https://www.gstatic.com/firebasejs/11.4.0/firebase-auth.js";
// import { getFirestore } from "https://www.gstatic.com/firebasejs/11.4.0/firebase-firestore.js";

// // Firebase Configuration (Replace with your actual Firebase settings)
// const firebaseConfig = {
//     apiKey: "AIzaSyAGD9PtR-pl-Eq3Ww4m9oz7g6d8DFms0DQ",
//     authDomain: "smart-waste-smart-access-a425c.firebaseapp.com",
//     projectId: "smart-waste-smart-access-a425c",
//     storageBucket: "smart-waste-smart-access-a425c.appspot.com",
//     messagingSenderId: "162639196066",
//     appId: "1:162639196066:web:5f0dc3feef24a78c520cfb"
// };

// // Initialize Firebase
// const app = initializeApp(firebaseConfig);
// const auth = getAuth(app);
// const db = getFirestore(app);

// // Export for other scripts
// export { auth, db };

 // Import Firebase modules
 import { initializeApp } from "https://www.gstatic.com/firebasejs/11.4.0/firebase-app.js";
 import { getAuth } from "https://www.gstatic.com/firebasejs/11.4.0/firebase-auth.js";
 import { getFirestore } from "https://www.gstatic.com/firebasejs/11.4.0/firebase-firestore.js";

const firebaseConfig = {
  apiKey: "AIzaSyAnY3P1JJBP6DigzoyrLw1Zikj1fH_occA",
  authDomain: "smart-waste-c39ac.firebaseapp.com",
  projectId: "smart-waste-c39ac",
  databaseURL: "https://smart-waste-c39ac-default-rtdb.firebaseio.com/",
  storageBucket: "smart-waste-c39ac.firebasestorage.app",
  messagingSenderId: "645631527511",
  appId: "1:645631527511:web:96117a712c70e3231ef112",
  measurementId: "G-YNWWZDNHZZ"
};

 // Initialize Firebase
 const app = initializeApp(firebaseConfig);
 const auth = getAuth(app);
 const db = getFirestore(app);

 // Export for other scripts
 export { auth, db };