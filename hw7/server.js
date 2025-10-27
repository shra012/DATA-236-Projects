require('dotenv').config();
const express = require('express');
const authRoutes = require('./authRoutes');

const app = express();
app.use(express.json());
app.use('/api/auth', authRoutes);
app.get('/health', (req, res) => res.json({ status: 'ok' }));

module.exports = app;
