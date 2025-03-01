// Express on port 9000 + socketio server
const WIDTH = 80;
const HEIGHT = 60;

// Express
const express = require('express');
const app = express();
const server = require('http').createServer(app);
const io = require('socket.io')(server);

// Express
app.use(express.static(__dirname + '/Visu'));

app.get('/', (req, res) => {
    res.sendFile(__dirname + '/Visu/index.html');
})

server.listen(9000, () => {
    console.log('Express server listening on port 9000');
})

// Socketio
io.on('connection', (socket) => {
    console.log('Socketio client connected');

    socket.on('disconnect', () => {
        console.log('Socketio client disconnected');
    })
})


// Connect to 3DCAM using socketio client
const iocli = require("socket.io-client");

const troisdcam = iocli('http://100.101.146.77:8000');

troisdcam.on('connect', () => {
    console.log('Connected to 3DCAM!');
    troisdcam.emit('join', 'BLOBS')
})

troisdcam.on('disconnect', () => {
    console.log('Disconnected from 3DCAM!');
})

troisdcam.on('error', () => {
    console.log('Error!');
})

troisdcam.on('3Dcam-VISU', (data) => {
  console.log('3Dcam-VISU', data);
  io.emit('3Dcam-VISU', data);
})

troisdcam.on('3Dcam-BLOBS', (data) => {
    console.log('3Dcam-BLOBS', data);
    io.emit('3Dcam-BLOBS', data);
})