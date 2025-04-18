const express = require('express');
const path = require('path');

const app = express();
const port = 80;

// Serve static files (CSS, JS, images) from smart-waste folder
app.use(express.static(__dirname));

// Serve HTML from the templates folder
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'templates', 'index.html'));
});

app.listen(80, '0.0.0.0', () => {
    console.log('Server is running on http://192.168.50.253:80');
});
