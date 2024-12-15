// Import required modules
const express = require('express');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');
const cors = require('cors');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
require('dotenv').config(); // Import dotenv to load environment variables

// Initialize the app
const app = express();
const PORT = 5000;
const JWT_SECRET = "your_jwt_secret_key"; // Replace with a secure key in production

// Middleware
app.use(cors());
app.use(bodyParser.json());

// MongoDB connection
mongoose.connect(process.env.MONGODB_URI, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
})
.then(() => console.log('Connected to MongoDB'))
.catch(err => console.error('Error connecting to MongoDB:', err));

// User Schema and Model
const userSchema = new mongoose.Schema({
    email: { type: String, required: true, unique: true },
    password: { type: String, required: true },
    userType: { type: String, enum: ['model', 'customer'], required: true },
});

const User = mongoose.model('User', userSchema);

// Routes

// Sign-in route
app.post('/api/signin', async (req, res) => {
    const { email, password } = req.body;

    try {
        const user = await User.findOne({ email });
        if (!user) {
            return res.status(400).json({ success: false, message: 'Invalid credentials' });
        }

        const isMatch = await bcrypt.compare(password, user.password);
        if (!isMatch) {
            return res.status(400).json({ success: false, message: 'Invalid credentials' });
        }

        // Generate JWT (optional)
        const token = jwt.sign({ userId: user._id }, JWT_SECRET, { expiresIn: '1h' });

        res.json({
            success: true,
            user: { email: user.email, userType: user.userType },
            token,
        });
    } catch (error) {
        console.error('Error during sign-in:', error);
        res.status(500).json({ success: false, message: 'Server error' });
    }
});

// Sign-up route (optional for future)
app.post('/api/signup', async (req, res) => {
    const { email, password, userType } = req.body;

    try {
        const existingUser = await User.findOne({ email });
        if (existingUser) {
            return res.status(400).json({ success: false, message: 'Email already registered' });
        }

        const hashedPassword = await bcrypt.hash(password, 10);
        const newUser = new User({ email, password: hashedPassword, userType });
        await newUser.save();

        res.json({ success: true, message: 'User registered successfully' });
    } catch (error) {
        console.error('Error during sign-up:', error);
        res.status(500).json({ success: false, message: 'Server error' });
    }
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
