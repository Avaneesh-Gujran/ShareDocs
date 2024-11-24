const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
    cors: {
        origin: "*", // Allow all origins (adjust in production)
        methods: ["GET", "POST"]
    }
});

// Store document state in memory (for simplicity)
const documents = {};

// Handle WebSocket connections
io.on('connection', (socket) => {
    console.log(`User connected: ${socket.id}`);

    // User joins a document room
    socket.on('joinDocument', (documentId) => {
        socket.join(documentId);
        console.log(`User ${socket.id} joined document ${documentId}`);

        // Send the current document state to the user
        if (!documents[documentId]) {
            documents[documentId] = { content: "", cursors: {} };
        }
        socket.emit('documentState', documents[documentId]);
    });

    // Handle content updates
    socket.on('contentUpdate', ({ documentId, content }) => {
        if (documents[documentId]) {
            documents[documentId].content = content;
            // Broadcast the update to all other users in the room
            socket.to(documentId).emit('contentUpdate', content);
        }
    });

    // Handle cursor updates
    socket.on('cursorUpdate', ({ documentId, userId, cursorPosition }) => {
        if (documents[documentId]) {
            documents[documentId].cursors[userId] = cursorPosition;
            // Broadcast the cursor position to all other users in the room
            socket.to(documentId).emit('cursorUpdate', { userId, cursorPosition });
        }
    });

    // Handle disconnection
    socket.on('disconnect', () => {
        console.log(`User disconnected: ${socket.id}`);
    });
});

// Start the server
const PORT = 3000;
server.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
