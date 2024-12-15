const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const bodyParser = require('body-parser');

// MongoDB connection URI
const uri = 'mongodb+srv://themodelhq:<trinityX1@>@cluster0.gn037.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0';

// MongoDB connection
mongoose.connect(uri, { useNewUrlParser: true, useUnifiedTopology: true })
  .then(() => console.log('Connected to MongoDB'))
  .catch(err => console.error('Failed to connect to MongoDB:', err));

// User schema
const userSchema = new mongoose.Schema({
  email: { type: String, required: true },
  password: { type: String, required: true },
  userType: { type: String, required: true }
});

const User = mongoose.model('User', userSchema);

const app = express();
const port = 5000;

app.use(cors());
app.use(bodyParser.json());

// Sign-in endpoint
app.post('/api/signin', async (req, res) => {
  const { email, password } = req.body;
  try {
    const user = await User.findOne({ email, password });
    if (user) {
      res.json({ success: true, user });
    } else {
      res.json({ success: false, message: 'Invalid credentials' });
    }
  } catch (error) {
    res.json({ success: false, message: 'Error signing in' });
  }
});

app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});
