const express = require('express');
const admin = require('firebase-admin');
const path = require('path');
const MikroNode = require('mikronode-ng');
const { spawn } = require('child_process');
const cors = require('cors');
const app = express();
const port = 80;

const MikroNode = require('mikronode-ng');

const device = new MikroNode('192.168.50.1');
device.connect('admin', '1234')  // Replace with correct password
    .then(([login]) => {
        console.log('Connection successful');
        login.close();
    })
    .catch(err => {
        console.error('Error connecting to MikroTik:', err);
    });

//==========================================================================

// Function to get MAC address from MikroTik given the client IP
async function getMacAddressFromIp(clientIp) {
    return new Promise((resolve, reject) => {
        const device = new MikroNode('192.168.50.1');
        device.connect('admin', '1234')
            .then(([login]) => {
                const chan = login.openChannel('dhcp-lease');
                chan.write('/ip/dhcp-server/lease/print');

                chan.on('done', (data) => {
                    console.log('MikroTik DHCP Leases:', data);  // Log the data
                    const leases = MikroNode.parseItems(data);
                    const matchedLease = leases.find(lease => lease.address === clientIp);

                    if (matchedLease) {
                        resolve(matchedLease['mac-address']);
                    } else {
                        resolve(null);
                    }
                    login.close();
                });

                chan.on('error', (err) => {
                    console.error('Channel error', err);
                    reject(err);
                    login.close();
                });
            })
            .catch(err => {
                console.error('Connection error', err);
                reject(err);
            });
    });
}

// ======================================================================
// New route to display IP and MAC
app.get('/connected-info', async (req, res) => {
    const clientIp = req.headers['x-forwarded-for'] || req.connection.remoteAddress;

    try {
        const macAddress = await getMacAddressFromIp(clientIp);

        if (macAddress) {
            res.send(`
                <h1>Connected Device Info</h1>
                <p><strong>IP Address:</strong> ${clientIp}</p>
                <p><strong>MAC Address:</strong> ${macAddress}</p>
            `);
        } else {
            res.send(`
                <h1>Device Info Not Found</h1>
                <p><strong>IP Address:</strong> ${clientIp}</p>
                <p><strong>MAC Address:</strong> Not found in DHCP leases.</p>
            `);
        }
    } catch (error) {
        res.status(500).send('Error fetching device info.');
    }
});

// Start the server and run all scripts
app.listen(port, '0.0.0.0', () => {
    console.log(`Server is running at http://192.168.50.252:${port}`);
    startAllScripts();
  });
  