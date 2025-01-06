const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');
const path = require('path');

const app = express();
const PORT = 3000;
const PYTHON_SERVER_URL = "https://expert-space-journey-694xgqx9gxvvfr45-3000.app.github.dev/"; // Python server base URL

app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'public')));

// Route to handle command execution
app.post('/execute-command', async (req, res) => {
    const { command } = req.body;

    try {
        // Forward the command to the Python script
        const response = await axios.post(`${PYTHON_SERVER_URL}/execute`, { command });
        res.json(response.data);
    } catch (error) {
        console.error('Error communicating with Python server:', error.message);
        res.status(500).json({ error: 'Failed to execute command' });
    }
});

// Route to fetch user, host, and directory info
app.get('/get-info', async (req, res) => {
    try {
        const response = await axios.get(`${PYTHON_SERVER_URL}/info`);
        res.json(response.data);
    } catch (error) {
        console.error('Error communicating with Python server:', error.message);
        res.status(500).json({ error: 'Failed to fetch user info' });
    }
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});
