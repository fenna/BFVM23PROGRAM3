const fs = require('fs');
const WebSocket = require('ws');

// Create WebSocket server
const wss = new WebSocket.Server({ port: 8080 });

// Function to send data to the client with a delay
function sendDataWithDelay(data, ws) {
    let index = 0;
    const interval = setInterval(() => {
        if (index < data.length) {
            ws.send(data[index]);
            index++;
        } else {
            clearInterval(interval);
        }
    }, 100);
}

// Handle WebSocket connection
wss.on('connection', ws => {
    console.log('Client connected');
    
    const filePath = 'Person1.csv';
    
    // Read CSV file
    fs.readFile(filePath, { encoding: 'utf-8' }, (err, data) => {
        if (err) {
            console.error('Error reading file:', err);
            return;
        }
        
        // Split data into lines
        const lines = data.split(/\r?\n/);
        
        // Send each line with a delay of one second
        sendDataWithDelay(lines, ws);
    });
});

console.log('WebSocket server running on port 8080');
