require('dotenv').config();
const jwt = require('jsonwebtoken');

const verifyToken = (req, res, next) => {
    const bearerHeader = req.headers['authorization'];

    if (typeof bearerHeader === 'undefined' || !bearerHeader.startsWith('Bearer ')) {
        return res.status(401).json({ message: "Unauthorized: Bearer token format required." });
    }

    const token = bearerHeader.split(' ')[1];
        
    jwt.verify(token, process.env.JWT_SECRET, (err, decoded) => {
        if (err) {
            return res.status(403).json({ 
                message: "Forbidden: Invalid or expired token.",
                errorName: err.name 
            }); 
        }
        req.user = decoded; 
        next();
    });
};

module.exports = verifyToken;