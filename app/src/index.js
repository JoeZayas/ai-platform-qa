require('dotenv').config();
const express = require('express');
const cors = require('cors');
const rateLimit = require('express-rate-limit');
const jwt = require('jsonwebtoken');
const axios = require('axios');
const path = require('path');
const companies = require('./data/companies');

const app = express();
const PORT = process.env.PORT || 3000;
const JWT_SECRET = process.env.JWT_SECRET || 'test-secret';

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '../public')));

// BUG-004: Rate limiter set too aggressively (3 requests/min)
const limiter = rateLimit({
  windowMs: 60 * 1000,
  max: 3,
  message: 'Too many requests from this IP'
});
app.use('/companies/', limiter);

// Helper function to verify JWT
const verifyToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }

  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    req.user = decoded;
    next();
  } catch (err) {
    return res.status(403).json({ error: 'Invalid token' });
  }
};

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    version: '1.0.0'
  });
});

// POST /auth/login - Authenticate user
app.post('/auth/login', (req, res) => {
  const { username, password } = req.body;

  if (username === 'qa_user' && password === 'test123') {
    const token = jwt.sign(
      { username, id: 'user-1' },
      JWT_SECRET,
      { expiresIn: '24h' }
    );
    return res.json({ token, user: { username, id: 'user-1' } });
  }

  res.status(401).json({ error: 'Invalid credentials' });
});

// GET /companies/search?q={query} - Search companies
// BUG-001: Search is case-sensitive (should be case-insensitive)
app.get('/companies/search', (req, res) => {
  const { q } = req.query;

  if (!q) {
    return res.json([]);
  }

  // BUG-001: This is case-sensitive - should convert to lowercase for comparison
  const results = companies.filter(company =>
    company.name.includes(q) ||
    company.industry.includes(q)
  );

  res.json(results);
});

// GET /companies/:dunsNumber - Get company details
app.get('/companies/:dunsNumber', verifyToken, (req, res) => {
  const { dunsNumber } = req.params;
  const company = companies.find(c => c.dunsNumber === dunsNumber);

  if (!company) {
    return res.status(404).json({ error: 'Company not found' });
  }

  res.json(company);
});

// GET /companies/:dunsNumber/credit-score - Get credit score
// BUG-002: Returns 200 with empty data for invalid DUNS instead of 404
app.get('/companies/:dunsNumber/credit-score', verifyToken, (req, res) => {
  const { dunsNumber } = req.params;
  const company = companies.find(c => c.dunsNumber === dunsNumber);

  if (!company) {
    // BUG-002: Should return 404, but returns 200 with empty data
    return res.json({ creditScore: null, riskLevel: null });
  }

  res.json({
    dunsNumber,
    creditScore: company.creditScore,
    riskLevel: company.riskLevel,
    debtRatio: Math.random() * 0.8,
    paymentHistory: 'Good'
  });
});

// POST /companies/:dunsNumber/insights - Trigger agent insight generation
// BUG-003: No input validation - accepts empty/malformed body
app.post('/companies/:dunsNumber/insights', verifyToken, async (req, res) => {
  try {
    const { dunsNumber } = req.params;
    // BUG-003: No validation of request body

    const company = companies.find(c => c.dunsNumber === dunsNumber);
    if (!company) {
      return res.status(404).json({ error: 'Company not found' });
    }

    // Call the agent endpoint
    const agentResponse = await axios.post(
      `http://localhost:${PORT === 3000 ? 3001 : 3000}/agent/insight`,
      { dunsNumber },
      { timeout: 20000 }
    );

    res.json({
      insight: agentResponse.data.insight,
      sources: ['Internal API', 'LangGraph Agent'],
      agentSteps: agentResponse.data.steps.length,
      runId: agentResponse.data.runId
    });
  } catch (error) {
    console.error('Error generating insight:', error.message);
    res.status(500).json({
      error: 'Failed to generate insight',
      message: error.message
    });
  }
});

// GET /agent/trace/:runId - Get LangSmith trace URL
app.get('/agent/trace/:runId', (req, res) => {
  const { runId } = req.params;
  res.json({
    runId,
    traceUrl: `https://smith.langchain.com/public/00000000-0000-0000-0000-000000000000/r/${runId}`
  });
});

app.listen(PORT, () => {
  console.log(`✓ App server running on http://localhost:${PORT}`);
});

module.exports = app;
