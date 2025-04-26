import { auth, db } from "../config/firebase-config.js";
import { doc, setDoc, getDoc } from "https://www.gstatic.com/firebasejs/11.4.0/firebase-firestore.js";

// Wait until the DOM is fully loaded
document.addEventListener("DOMContentLoaded", function () {
    const guestButton = document.getElementById("guest-btn");
    const insertBottleButton = document.getElementById("insert-bottle-btn");

    if (guestButton) {
        guestButton.addEventListener("click", async (event) => {
            event.preventDefault(); // Prevent default action for the <a> tag

            let deviceID = localStorage.getItem('deviceID');

            if (!deviceID) {
                try {
                    // Ensure FingerprintJS is properly loaded
                    const fp = await FingerprintJS.load();
                    const result = await fp.get();
                    const deviceUniqueID = result.visitorId; // This creates a unique device ID

                    // Store the device ID in localStorage to track this device
                    localStorage.setItem('deviceID', deviceUniqueID);

                    // Now create a new guest account in Firestore
                    createGuestAccount(deviceUniqueID);
                } catch (error) {
                    console.error("Error loading FingerprintJS:", error);
                }
            } else {
                alert("You are already logged in as a guest on this device.");
                window.location.href = "guest-dashboard.html";  // Redirect to the guest dashboard
            }
        });
    }

    // Function to create a new guest account in Firestore
    async function createGuestAccount(deviceID) {
        try {
            await setDoc(doc(db, "Users Collection", deviceID), {
                GuestID: deviceID,
                TotalBottlesDeposited: 0,
                WiFiTimeAvailable: 0.0,
                DeviceInfo: deviceID,
                SessionStartTime: new Date().toISOString(),
                SessionEndTime: null
            });

            alert("Guest account created successfully!");
            window.location.href = "guest-dashboard.html";  // Redirect to guest dashboard
        } catch (error) {
            console.error("Error creating guest account:", error);
            alert("Error: " + error.message);
        }
    }

    // Handle "Insert Bottle" functionality
    if (insertBottleButton) {
        insertBottleButton.addEventListener("click", async () => {
            let deviceID = localStorage.getItem('deviceID');

            if (deviceID) {
                const guestRef = doc(db, "Users Collection", deviceID);
                const guestSnap = await getDoc(guestRef);

                if (guestSnap.exists()) {
                    const currentWiFiTime = guestSnap.data().WiFiTimeAvailable;
                    const newWiFiTime = currentWiFiTime + 10; // Add 10 minutes

                    await setDoc(guestRef, {
                        WiFiTimeAvailable: newWiFiTime
                    }, { merge: true });

                    alert("Wi-Fi time has been added to your account!");
                    window.location.href = "guest-dashboard.html";
                }
            } else {
                alert("No guest account found. Please create a guest account first.");
            }
        });
    }
});
