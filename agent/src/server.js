import 'dotenv/config.js';
import express from 'express';
import { runInsightAgent } from './index.js';

const app = express();
const PORT = 3001;

app.use(express.json());

app.post('/agent/insight', async (req, res) => {
  try {
    const { dunsNumber } = req.body;

    if (!dunsNumber) {
      return res.status(400).json({ error: 'dunsNumber is required' });
    }

    const result = await runInsightAgent(dunsNumber);

    if (result.error) {
      return res.status(500).json({
        error: result.error,
        insight: result.insight,
        runId: result.runId,
        steps: result.steps
      });
    }

    res.json({
      insight: result.insight,
      runId: result.runId,
      steps: result.steps
    });
  } catch (error) {
    console.error('Error in /agent/insight:', error);
    res.status(500).json({
      error: error.message,
      insight: null,
      runId: null,
      steps: []
    });
  }
});

app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'agent' });
});

app.listen(PORT, () => {
  console.log(`✓ Agent server running on http://localhost:${PORT}`);
});
