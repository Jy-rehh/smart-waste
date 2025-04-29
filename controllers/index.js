// index.js
import { db } from "../config/firebase-config.js";
import { collection, query, where, getDocs } from "https://www.gstatic.com/firebasejs/10.11.0/firebase-firestore.js";

async function fetchActiveUsers() {
    const usersCol = collection(db, "Users Collection");
    const q = query(usersCol, where("status", "==", "active"));

    try {
        const querySnapshot = await getDocs(q);
        querySnapshot.forEach((doc) => {
            const data = doc.data();
            console.log(`MAC: ${data.macAddress}, IP: ${data.ipAddress}`);
            updateStatusCard(data.macAddress, data.ipAddress);
        });
    } catch (error) {
        console.error("Error fetching users:", error);
    }
}

function updateStatusCard(mac, ip) {
    const statusElement = document.querySelector(".status");
    const ipElement = document.querySelector(".ip");
    
    if (mac && ip) {
        statusElement.innerHTML = `<span class="icon">&#128246;</span> <span class="connected">Connected</span>`;
        ipElement.textContent = `IP: ${ip} | MAC: ${mac}`;
    } else {
        statusElement.innerHTML = `<span class="icon">&#128246;</span> <span class="disconnected">Disconnected</span>`;
        ipElement.textContent = `IP: | MAC: `;
    }
}

// Call it when page loads
fetchActiveUsers();
