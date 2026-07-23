const express = require('express');
const { Pool } = require('pg');
const path = require('path');

const app = express();
app.use(express.json());

// Serve static files from the 'public' folder
app.use(express.static(path.join(__dirname, 'public')));

const pool = new Pool({
    host: process.env.DB_HOST,
    user: process.env.DB_USER,
    password: process.env.DB_PASS,
    database: process.env.DB_NAME,
    port: 5432,
});

// Wait for Postgres to be ready before accepting traffic (handles the case
// where the web-app container starts before the db container finishes init)
async function waitForDb(retries = 20, delayMs = 1500) {
    for (let i = 1; i <= retries; i++) {
        try {
            await pool.query('SELECT 1');
            console.log('Connected to database.');
            return;
        } catch (err) {
            console.log(`DB not ready yet (attempt ${i}/${retries}): ${err.message}`);
            await new Promise((r) => setTimeout(r, delayMs));
        }
    }
    console.error('Could not connect to database after retries. Exiting.');
    process.exit(1);
}

// BACKEND: OWASP Top 10 Proactive Controls C7 (Level 1) — Password verification
async function verifyPasswordBackend(password) {
    // Check lengths (Min 8, Max 64 per OWASP recommendations)
    if (!password || password.length < 8 || password.length > 64) {
        return { valid: false, message: 'Password must be between 8 and 64 characters.' };
    }

    // Check against 100k common/breached dictionary
    const query = 'SELECT 1 FROM common_passwords WHERE password = $1';
    const result = await pool.query(query, [password]);

    if (result.rowCount > 0) {
        return { valid: false, message: 'Password is too common. Please choose a unique password.' };
    }

    return { valid: true, message: 'Password meets all requirements.' };
}

app.post('/api/register', async (req, res) => {
    const { username, password } = req.body;

    if (!username || typeof username !== 'string' || username.trim().length === 0) {
        return res.status(400).json({ success: false, message: 'Username is required.' });
    }

    const validation = await verifyPasswordBackend(password);

    if (!validation.valid) {
        // Fails requirement -> return error (Frontend stays on home page)
        return res.status(400).json({ success: false, message: validation.message });
    }

    try {
        // Log to table 2400968 (username + creation time only, NO password)
        await pool.query('INSERT INTO "2400968" (username) VALUES ($1)', [username.trim()]);
        console.log(`Logged account creation for user: ${username.trim()}`);
        res.json({ success: true });
    } catch (error) {
        console.error('DB insert error:', error.message);
        res.status(500).json({ success: false, message: 'Server database error.' });
    }
});

// Explicit route for home page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

waitForDb().then(() => {
    app.listen(3000, () => console.log('Server running on port 3000'));
});
