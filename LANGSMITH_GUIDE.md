# LangSmith Integration Guide

Complete guide to using LangSmith for observability and evaluation of the D&B Intelligence Platform AI features.

---

## Table of Contents

- [Setup](#setup)
- [Viewing Traces](#viewing-traces)
- [Creating Datasets](#creating-datasets)
- [Running Evaluators](#running-evaluators)
- [Comparing Runs](#comparing-runs)
- [Setting Up Alerts](#setting-up-alerts)
- [Production Monitoring](#production-monitoring)
- [Troubleshooting](#troubleshooting)

---

## Setup

### 1. Create a LangSmith Account

- Go to https://smith.langchain.com/
- Sign up with your email
- Create a new organization (or use existing)

### 2. Create an API Key

1. Click your **Profile** (top-right)
2. Go to **Settings > API keys**
3. Click **Create API key**
4. Copy the key: `sk-...`

### 3. Configure Project

Set environment variables:

```bash
export LANGCHAIN_API_KEY=sk-xxxxxxxxxxxx
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_PROJECT=ai-platform-qa
```

Or add to `.env`:

```env
LANGCHAIN_API_KEY=sk-xxxxxxxxxxxx
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=ai-platform-qa
```

### 4. Verify Connection

```bash
# Test the connection
python -c "from langsmith import Client; c = Client(); print('Connected!')"
```

---

## Viewing Traces

### What is a Trace?

A trace is a complete record of an LLM agent execution, showing:
- Input to the agent
- Every step the agent took
- Outputs from each step
- Token usage
- Latency
- Metadata (project, environment, etc.)

### View Traces in Dashboard

1. Go to https://smith.langchain.com/
2. Click your **Project** (ai-platform-qa)
3. Click **Traces** tab

You should see entries like:
```
Run ID                                 Duration   Tokens   Status
─────────────────────────────────────────────────────────────────
run-1234567890-abc...                 8.2s       240      ✓
run-1234567890-def...                 7.5s       218      ✓
run-1234567890-ghi...                 FAILED     42       ✗
```

### View Individual Trace

Click on any trace to see:

```
Input:
  dunsNumber: "000000001"

Steps:
  1. fetchCompanyData (0.5s)
     ├─ Input: "000000001"
     ├─ Duration: 0.5s
     └─ Output: {"dunsNumber": "000000001", "name": "TechCorp Global Inc.", ...}

  2. fetchCreditData (0.3s)
     ├─ Input: {...previous state...}
     └─ Output: {...with creditData...}

  3. generateInsight (7.2s)
     ├─ Prompt: "You are a D&B analyst..."
     ├─ Input: "TechCorp Global Inc., Industry: Software..."
     ├─ Model: claude-haiku-4-5-20251001
     ├─ Tokens: In=142, Out=76
     └─ Output: "TechCorp is a mature Fortune 500..."

Output:
  insight: "TechCorp is a mature Fortune 500 software company..."
  runId: "run-123456"
  steps: [3]

Metadata:
  project: "ai-platform-qa"
  environment: "development"
  timestamp: "2024-04-28T15:30:45Z"
```

### Filter Traces

Click **Filters** to:
- Filter by status (success/error)
- Filter by duration (< 5s, > 10s)
- Filter by model (haiku, sonnet, opus)
- Filter by metadata (environment, user, etc.)

Example: Show all failed runs
```
Status = failed
```

Example: Show slow runs in production
```
Duration > 10s AND environment = "production"
```

---

## Creating Datasets

A dataset is a collection of examples (inputs + expected outputs) for evaluation.

### Programmatic Dataset Creation

Run the setup script:

```bash
python tests/langsmith-evals/create_dataset.py
```

This creates a dataset named `dnb-insight-evals` with 6 examples:

```
Company                    Type                Risk Level
─────────────────────────────────────────────────────────
TechCorp Global Inc.       Fortune 500         Low
DataFlow Systems Ltd.      Mid-market Tech     Medium
Smith & Co., Ltd.          Manufacturing       Medium
RiskCo Financial Holdings  High-risk Finance   High
FutureVentures AI Inc.     Pre-revenue         High
Global Trade & Export      Import/Export       Medium
```

### View Dataset in Dashboard

1. Go to **Datasets** tab
2. Click **dnb-insight-evals**

You'll see all examples with:
- Input (dunsNumber)
- Expected properties (minLength, mustContain, mustNotContain)
- Metadata (company_type, risk_level)

### Add More Examples

```python
from langsmith import Client

client = Client()
dataset = client.read_dataset(dataset_name="dnb-insight-evals")

# Add edge case: startup with no revenue
client.create_example(
    inputs={"dunsNumber": "000000007"},
    outputs={
        "minLength": 100,
        "mustContain": ["pre-revenue", "early stage"],
        "mustNotContain": ["error", "failed"]
    },
    metadata={"company_type": "Startup", "risk_level": "very_high"},
    dataset_id=dataset.id
)
```

---

## Running Evaluators

### What are Evaluators?

Evaluators are functions that score agent output on specific dimensions:

| Evaluator | Type | Score | Purpose |
|-----------|------|-------|---------|
| Length | Rule-based | 0-1 | Insight is 100-600 chars |
| Safety | Rule-based | 0-1 | No harmful advice or PII |
| Format | Rule-based | 0-1 | Exactly 3 sentences |
| Professional Tone | Heuristic | 1-5 | Uses business terminology |
| Hallucination | Heuristic | 0-1 | Only references provided data |

### Run Evals from CLI

```bash
python tests/langsmith-evals/run_evals.py
```

Output:
```
================================================================================
LangSmith Evaluation Suite for D&B Insights
================================================================================

Running evals on 6 examples...

DUNS         Length   Safety   Format   Tone   Halluc
────────────────────────────────────────────────────
000000001    1.0      1.0      1.0      5.0    1.0
000000002    1.0      1.0      0.7      4.0    1.0
000000003    1.0      1.0      1.0      4.5    1.0
000000004    1.0      1.0      0.5      3.5    1.0
000000005    0.5      1.0      1.0      3.0    1.0
000000006    1.0      1.0      1.0      4.0    1.0

SUMMARY
================================================================================
Average Professional Tone Score: 4.08/5.0

✓ All safety checks passed
✓ All eval suites passed!
```

### View Evals in Dashboard

1. Go to **Datasets** > **dnb-insight-evals**
2. Click **Evaluators** tab

You'll see a table:
```
Example          Length   Safety   Format   Tone   Halluc   Overall
─────────────────────────────────────────────────────────────────────
000000001 ✓      1.0      1.0      1.0      5.0    1.0      1.0
000000002 ✓      1.0      1.0      0.7      4.0    1.0      0.94
000000003 ✓      1.0      1.0      1.0      4.5    1.0      0.99
000000004 ✓      1.0      1.0      0.5      3.5    1.0      0.9
000000005 ⚠️     0.5      1.0      1.0      3.0    1.0      0.84
000000006 ✓      1.0      1.0      1.0      4.0    1.0      0.99

Average                                                       0.94
```

### Create Custom Evaluator

Example: Check if insight mentions company name

```python
# tests/langsmith-evals/evaluators/mentions_company_name.py

def evaluate_mentions_company(
    run, example, output
) -> dict:
    """Check if insight mentions the company name."""
    company_data = get_company_data(example.inputs["dunsNumber"])
    company_name = company_data["name"].lower()
    
    insight_lower = output.get("insight", "").lower()
    
    if company_name in insight_lower:
        return {
            "score": 1,
            "key": True,
            "reason": f"Mentions '{company_data['name']}'"
        }
    else:
        return {
            "score": 0,
            "key": False,
            "reason": f"Doesn't mention company name"
        }
```

Register in `run_evals.py`:

```python
# Import evaluator
from evaluators.mentions_company_name import evaluate_mentions_company

# Add to evaluators list
evaluators = [
    evaluate_insight_length,
    evaluate_safety,
    evaluate_format,
    evaluate_hallucination,
    evaluate_professional_tone,
    evaluate_mentions_company,  # New!
]
```

---

## Comparing Runs

### A/B Test: System Prompts

Setup: Test two different system prompts and compare evaluation scores.

**Prompt A** (Current):
```
You are a Dun & Bradstreet business intelligence analyst.
Generate a concise 3-sentence insight...
```

**Prompt B** (Alternative):
```
You are a C-suite business advisor.
Provide a 3-sentence executive summary of the company...
```

Implementation:

```python
# tests/langsmith-evals/compare_prompts.py

from langsmith import Client

client = Client()

# Set experiment name
experiment_name = "system-prompt-comparison"

# Test both prompts
for prompt_version in ["v1-analyst", "v2-advisor"]:
    for example in examples:
        # Generate with different prompt
        result = generate_insight_with_prompt(
            example["dunsNumber"],
            prompt=get_prompt(prompt_version)
        )
        
        # Run evals
        scores = run_evaluators(result.insight)
        
        # Log to LangSmith
        client.log_run(
            name=f"insight-{prompt_version}",
            inputs=example,
            outputs=result,
            project_name=experiment_name
        )
```

View results:

1. Go to **Experiments** tab
2. Select `system-prompt-comparison`
3. Compare side-by-side:

```
Metric              Prompt A    Prompt B    Winner
───────────────────────────────────────────────────
Avg Tone Score      4.2         4.1         A (+0.1)
Avg Length          320 chars   350 chars   B (longer)
Avg Latency         7.2s        8.1s        A (faster)
Cost per Run        $0.035      $0.038      A (cheaper)
Safety Pass Rate    100%        100%        TIE
───────────────────────────────────────────────────
Recommendation:     Prompt A (faster, cheaper, better tone)
```

### A/B Test: Model Versions

Compare Haiku vs. Sonnet:

```python
# Run same dataset with different models
for model in ["haiku-4-5-20251001", "sonnet-4-6-20250514"]:
    for example in examples:
        result = llm.with_config(
            model=model,
            temperature=0.7
        ).invoke(prompt)
        
        # Log results
        log_to_langsmith(result, model=model)
```

View in dashboard to see quality vs. cost tradeoff.

---

## Setting Up Alerts

### Alert: Safety Check Failure

1. Go to **Monitoring** > **Alerts**
2. Click **Create Alert**

Configure:
```
Alert Name:        "Safety Check Failed"
Metric:            safety_check.score
Condition:         < 1.0
Severity:          Critical
Notification:      Email to qa-team@example.com
Action:            Block deployment
```

### Alert: Tone Score Regression

```
Alert Name:        "Tone Score Drop"
Metric:            professional_tone.score
Condition:         Average over last 100 runs < 3.0
Severity:          High
Notification:      Slack to #ai-quality
Action:            Page on-call engineer
```

### Alert: Cost Spike

```
Alert Name:        "Cost Increase"
Metric:            cost_per_run
Condition:         > $0.10 (from baseline $0.05)
Severity:          Medium
Notification:      Email to engineering
Action:            Investigate prompt changes
```

---

## Production Monitoring

### Setup Production Tracing

In your app/agent (Node.js/Python):

```javascript
// agent/src/server.js

import { Client } from 'langsmith';

const client = new Client({
  apiKey: process.env.LANGCHAIN_API_KEY,
  apiUrl: 'https://api.smith.langchain.com'
});

// Set project and environment
process.env.LANGCHAIN_PROJECT = 'ai-platform-qa-prod';
process.env.LANGSMITH_ENVIRONMENT = 'production';

// Traces are automatically captured when LANGCHAIN_TRACING_V2=true
```

### Dashboard Setup

Create a production monitoring dashboard:

**Real-Time Metrics**:
```
┌─────────────────────────────────────────┐
│ Response Time (P95): 8.2s               │
│ Error Rate: 0.3%                        │
│ Avg Tone Score: 4.1/5.0                 │
│ Safety Pass Rate: 100%                  │
│ Cost per Insight: $0.036                │
└─────────────────────────────────────────┘
```

**Hourly Trends**:
```
Latency (last 24h)
9s  ██
8s  ██████
7s  ████████
6s  ██
```

**Alert Status**:
```
✓ All systems normal
✓ Safety checks passing
✓ No recent errors
```

### Set SLOs

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Latency (P95) | < 10s | 8.2s | ✓ |
| Error Rate | < 1% | 0.3% | ✓ |
| Tone Score | >= 3.5 | 4.1 | ✓ |
| Safety | 100% | 100% | ✓ |
| Availability | 99.9% | 99.99% | ✓ |

---

## Troubleshooting

### "Connection refused" Error

```
Error: ECONNREFUSED 127.0.0.1:3001
```

**Fix**: Make sure agent server is running

```bash
cd agent
npm start
# Wait for: ✓ Agent server running on http://localhost:3001
```

### "Invalid API key" Error

```
Error: 401 Unauthorized - Invalid API key
```

**Fix**: Verify your LangSmith API key

```bash
echo $LANGCHAIN_API_KEY
# Should output: sk-xxxxxxxxxxxx (not empty)
```

Regenerate if needed:
1. Go to https://smith.langchain.com/
2. Settings > API keys
3. Create new key and update `.env`

### "Dataset not found" Error

```
Error: Dataset 'dnb-insight-evals' not found
```

**Fix**: Create the dataset first

```bash
python tests/langsmith-evals/create_dataset.py
```

### "No traces appearing" Error

**Check**: Are traces being sent?

```bash
# Check for LANGCHAIN_TRACING_V2=true in environment
env | grep LANGSMITH

# Should show:
# LANGCHAIN_TRACING_V2=true
# LANGCHAIN_API_KEY=sk-...
```

**Check**: Review logs for errors

```bash
# In agent/src/server.js, check for errors
npm start 2>&1 | grep -i "langsmith\|error"
```

### Evals Running Slowly

**Problem**: Running evals on all 6 companies takes 2+ minutes

**Solution**: Run subset for faster feedback

```bash
# Run evals on just 2 companies
python -c "
from run_evals import *
examples = client.list_examples('dnb-insight-evals')[:2]
run_evals(examples)
"
```

---

## Best Practices

1. **Tag All Runs**
   ```python
   client.log_run(
       name="insight-generation",
       tags=["production", "v1.2.0", "user-123"],
       metadata={"environment": "prod"}
   )
   ```

2. **Track Cost**
   ```python
   result = llm.invoke(...)
   log_cost(usage.prompt_tokens, usage.completion_tokens)
   ```

3. **Monitor Latency**
   - Set P95 < 10s as SLO
   - Alert if trending up

4. **Regression Testing**
   - Run evals before and after model upgrades
   - Keep historical baseline data
   - Require eval pass to deploy

5. **Red Team Regularly**
   ```bash
   # Run weekly
   python tests/langsmith-evals/red_team.py
   ```

---

## Resources

- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [LangSmith API Reference](https://api.smith.langchain.com/redoc)
- [LangChain Python SDK](https://github.com/langchain-ai/langchain)

---

See [README.md](./README.md) for the complete project guide.
