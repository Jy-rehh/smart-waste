import { auth, db } from "../config/firebase-config.js";

// Fetch and display IP and MAC address
async function displayUserInfo() {
    try {
      const usersSnapshot = await db.collection('Users Collection').get();
      usersSnapshot.forEach(doc => {
        const userData = doc.data();
        const ipAddress = userData.ipAddress || 'Unknown IP';
        const macAddress = userData.macAddress || 'Unknown MAC';
  
        // Create the <p> elements
        const ipElement = document.createElement('p');
        ipElement.className = 'ip';
        ipElement.textContent = `IP: ${ipAddress} | MAC: ${macAddress}`;
  
        const remainingTimeElement = document.createElement('p');
        remainingTimeElement.className = 'remaining-time';
        remainingTimeElement.textContent = 'Remaining Time:';
  
        // Append them to the body (or any container you want)
        document.body.appendChild(ipElement);
        document.body.appendChild(remainingTimeElement);
      });
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  }
  
  // Call the function when page loads
  window.onload = displayUserInfo;