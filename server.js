const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');
const path = require('path');

const app = express();
const PORT = 3000;
const PYTHON_SERVER_URL = "http://localhost:5000"; // Update if Python server runs on a different URL in Codespaces

app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'public'))); // Serve the frontend files

// Route to fetch user, host, and directory info
app.get('/info', async (req, res) => {
    try {
        const response = await axios.get(`${PYTHON_SERVER_URL}/info`);
        res.json(response.data);
    } catch (error) {
        console.error('Error communicating with Python backend:', error.message);
        res.status(500).json({ error: 'Failed to fetch user info' });
    }
});

// Route to execute commands
app.post('/execute', async (req, res) => {
    try {
        const { command } = req.body;
        const response = await axios.post(`${PYTHON_SERVER_URL}/execute`, { command });
        res.json(response.data);
    } catch (error) {
        console.error('Error communicating with Python backend:', error.message);
        res.status(500).json({ error: 'Failed to execute command' });
    }
});

// Start the Node.js server
app.listen(PORT, () => {
    console.log(`Node.js server running at https://expert-space-journey-694xgqx9gxvvfr45-3000.app.github.dev/`);
});
