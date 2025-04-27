import { db } from "../config/firebase-config.js";  // Firestore configuration

async function displayUserInfo(macAddress) {
  try {
    // Fetch the user's document from Firestore by MAC address
    const docRef = db.collection('Users Collection').doc(macAddress);
    const docSnapshot = await docRef.get();

    // Check if the document exists
    if (docSnapshot.exists) {
      const userData = docSnapshot.data();
      const ipAddress = userData.ipAddress || 'Unknown IP';
      const mac = userData.macAddress || 'Unknown MAC';

      // Update the IP and MAC display
      const ipElement = document.querySelector('.ip');
      ipElement.textContent = `IP: ${ipAddress} | MAC: ${mac}`;
    } else {
      console.log("No user data found for this MAC address.");
    }
  } catch (error) {
    console.error('Error fetching user data:', error);
  }
}

// Example call with device's MAC address
const userMacAddress = "device-mac-address";  // Replace with actual MAC address
displayUserInfo(userMacAddress);
