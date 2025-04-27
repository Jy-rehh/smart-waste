import { db } from "../config/firebase-config.js";  // Import Firestore configuration

// Function to display the device's MAC and IP addresses
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

      // Create the <p> elements to display the IP and MAC addresses
      const ipElement = document.createElement('p');
      ipElement.className = 'ip';
      ipElement.textContent = `IP: ${ipAddress} | MAC: ${mac}`;

      const remainingTimeElement = document.createElement('p');
      remainingTimeElement.className = 'remaining-time';
      remainingTimeElement.textContent = 'Remaining Time:';

      // Append the elements to the body or any container you prefer
      document.body.appendChild(ipElement);
      document.body.appendChild(remainingTimeElement);
    } else {
      console.log("No user data found for this MAC address.");
    }
  } catch (error) {
    console.error('Error fetching user data:', error);
  }
}

// Example: Call the function with the device's MAC address
// You might get this MAC address from server-side logic or pass it in from a template engine
const userMacAddress = "device-mac-address";  // Replace with the actual MAC address of the device
displayUserInfo(userMacAddress);
