# AI Platform QA Testing Ecosystem

> A production-quality QA testing framework for AI-driven workflows and LangGraph agents, built to demonstrate advanced QA expertise for the Dun & Bradstreet Senior QA Automation Engineer role.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Test Strategy](#test-strategy)
- [Quick Start](#quick-start)
- [Setup Instructions](#setup-instructions)
- [Running Tests](#running-tests)
- [Project Structure](#project-structure)
- [Known Issues (Intentional Bugs)](#known-issues-intentional-bugs)
- [CI/CD Pipeline](#cicd-pipeline)
- [LangSmith Integration](#langsmith-integration)
- [Interview Preparation Guide](#interview-preparation-guide)

## Overview

This project simulates a **B2B data intelligence platform** (similar to Dun & Bradstreet's core product) and demonstrates comprehensive QA testing at every layer:

- **UI Testing**: Playwright with Python for browser automation and Page Object Model
- **API Testing**: REST endpoint validation with realistic edge cases
- **Agent Testing**: LangGraph workflow validation at the node and graph level
- **LLM Evaluation**: LangSmith-based evals for output quality, safety, and professionalism
- **Red Team Testing**: Adversarial testing for prompt injection, role override, PII, and scope creep

## Architecture

```
┌────────────────────────────────────────────────────────────┐
│                   Frontend Dashboard                        │
│                  (HTML/CSS/JavaScript)                      │
└────────────────────────┬─────────────────────────────────────┘
                         │ HTTP
                         ▼
┌────────────────────────────────────────────────────────────┐
│              Express.js API Server (port 3000)              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Endpoints:                                          │   │
│  │ • POST /auth/login                                  │   │
│  │ • GET  /companies/search                            │   │
│  │ • GET  /companies/:dunsNumber                       │   │
│  │ • GET  /companies/:dunsNumber/credit-score          │   │
│  │ • POST /companies/:dunsNumber/insights (triggers)   │   │
│  │ • GET  /agent/trace/:runId                          │   │
│  │ • GET  /health                                      │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────┬─────────────────────────────────────────┘
                     │ HTTP (localhost:3001)
                     ▼
┌────────────────────────────────────────────────────────────┐
│         LangGraph Agent Server (port 3001)                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ State Graph:                                        │   │
│  │  1. fetchCompanyData                                │   │
│  │  2. fetchCreditData                                 │   │
│  │  3. generateInsight (calls Claude API)              │   │
│  │  4. handleError (graceful error handling)           │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────┬─────────────────────────────────────────┘
                     │ API
                     ▼
        ┌────────────────────────┐
        │  Anthropic Claude API  │
        │  (haiku-4-5-20251001)  │
        └────────────────────────┘
                     
        ┌────────────────────────┐
        │  LangSmith (Tracing)   │
        │  (Observability Layer) │
        └────────────────────────┘
```

## Test Strategy

### Test Pyramid

```
                         ▲
                        ╱ ╲
                       ╱   ╲  LLM Evals (5%)
                      ╱─────╲
                     ╱       ╲
                    ╱         ╲  Agent Integration (15%)
                   ╱───────────╲
                  ╱             ╲
                 ╱               ╲  API Tests (40%)
                ╱─────────────────╲
               ╱                   ╲
              ╱                     ╲ UI Tests (40%)
             ╱───────────────────────╲
```

### Layer 1: UI Tests (40%)
- **Framework**: Playwright + Python + pytest
- **Scope**: Browser-based user workflows
- **Tests**:
  - Authentication (valid/invalid credentials)
  - Search functionality (case sensitivity, special chars)
  - Company detail display
  - AI insight generation (loading states, content validation)
- **File**: `tests/playwright/tests/ui/`

### Layer 2: API Tests (40%)
- **Framework**: Pytest + requests
- **Scope**: HTTP endpoint validation
- **Tests**:
  - Authentication (JWT tokens, expiry)
  - Search filtering and results
  - Company retrieval (404 handling, invalid DUNS)
  - Insight generation (timeouts, response validation)
  - Health checks
- **File**: `tests/playwright/tests/api/`

### Layer 3: Agent Integration (15%)
- **Framework**: Jest + Node.js
- **Scope**: LangGraph workflow validation
- **Tests**:
  - Graph structure (nodes, edges, state)
  - Node-level unit tests (mocked API calls)
  - State transitions between nodes
  - Error handling paths
  - Full-workflow integration (real API calls)
- **File**: `tests/agent-tests/`

### Layer 4: LLM Evals (5%)
- **Framework**: LangSmith SDK + Python
- **Scope**: Output quality, safety, and compliance
- **Evaluators**:
  - Length check (100-600 chars)
  - Professional tone (1-5 scale)
  - Hallucination detection
  - Safety validation (no harmful advice, PII)
  - Format check (exactly 3 sentences)
- **Red Team**: Prompt injection, role override, PII extraction, scope creep
- **File**: `tests/langsmith-evals/`

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- npm or yarn
- Anthropic API key
- LangChain/LangSmith API key

### 1-Minute Setup

```bash
# Clone and navigate
cd ai-platform-qa

# Install all dependencies
npm run install:all

# Copy environment variables
cp app/.env.example app/.env
cp agent/.env.example agent/.env

# Edit .env files with your API keys:
# - ANTHROPIC_API_KEY=sk-ant-...
# - LANGCHAIN_API_KEY=sk-...
```

### Run Tests

```bash
# Start the app (in one terminal)
npm start

# In another terminal, run all tests
npm run test:all

# Or run specific test suites:
npm run test:api      # API tests only
npm run test:ui       # UI tests only
npm run test:agents   # Agent tests only
npm run test:evals    # LangSmith evals only
npm run test:redteam  # Red team security tests
```

## Setup Instructions

### Step 1: Install Dependencies

```bash
# Install root dependencies
npm install

# Install app dependencies
cd app
npm install
cd ..

# Install agent dependencies
cd agent
npm install
cd ..

# Install test dependencies (Python)
pip install -r tests/requirements.txt
playwright install chromium firefox
```

### Step 2: Configure Environment Variables

**For the app** (`app/.env`):
```env
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx
LANGCHAIN_API_KEY=sk-xxxxxxxxxxxx
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=ai-platform-qa
NODE_ENV=development
PORT=3000
JWT_SECRET=your-secret-key
```

**For the agent** (`agent/.env`):
```env
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx
LANGCHAIN_API_KEY=sk-xxxxxxxxxxxx
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=ai-platform-qa
NODE_ENV=development
```

### Step 3: Start Services

```bash
# Terminal 1: Start Express app
cd app
npm start
# Output: ✓ App server running on http://localhost:3000

# Terminal 2: Start LangGraph agent (if running integration tests)
cd agent
npm start
# Output: ✓ Agent server running on http://localhost:3001
```

### Step 4: Verify Setup

```bash
# Health check
curl http://localhost:3000/health

# Should return:
# {"status":"ok","timestamp":"2024-04-28T...","version":"1.0.0"}
```

## Running Tests

### UI Tests

```bash
# Headless mode (CI)
pytest tests/playwright/tests/ui -v

# Headed mode (watch in browser)
pytest tests/playwright/tests/ui -v --headed

# Single test
pytest tests/playwright/tests/ui/test_auth.py::test_valid_credentials_show_dashboard -v

# Skip slow tests
pytest tests/playwright/tests/ui -v -m "not slow"
```

### API Tests

```bash
# All API tests
pytest tests/playwright/tests/api -v

# Single endpoint
pytest tests/playwright/tests/api/test_companies_api.py -v

# With coverage
pytest tests/playwright/tests/api --cov=tests
```

### Agent Tests

```bash
# All agent tests
npm run test:agents

# Single test file
npm run test:agents -- graph-structure.test.js

# With coverage
npm run test:agents -- --coverage
```

### LangSmith Evals

```bash
# Create dataset (one-time)
python tests/langsmith-evals/create_dataset.py

# Run evals
python tests/langsmith-evals/run_evals.py

# Run red team tests
python tests/langsmith-evals/red_team.py
```

### All Tests

```bash
npm run test:all
```

## Project Structure

```
ai-platform-qa/
├── app/                              # Express.js mock platform
│   ├── src/
│   │   ├── index.js                 # Main server + endpoints
│   │   └── data/
│   │       └── companies.js          # Mock company data (6 companies)
│   ├── public/
│   │   └── index.html               # Frontend dashboard
│   ├── package.json
│   ├── .env.example
│   └── README.md
│
├── agent/                            # LangGraph agent
│   ├── src/
│   │   ├── index.js                 # StateGraph definition
│   │   └── server.js                # Agent API server
│   ├── package.json
│   ├── .env.example
│   └── README.md
│
├── tests/                            # Test suites
│   ├── playwright/
│   │   ├── pages/                   # Page Object Model
│   │   │   ├── login_page.py
│   │   │   ├── dashboard_page.py
│   │   │   └── company_detail_page.py
│   │   └── tests/
│   │       ├── ui/                  # Browser automation tests
│   │       │   ├── test_auth.py
│   │       │   ├── test_search.py
│   │       │   ├── test_company_detail.py
│   │       │   └── test_ai_insights.py
│   │       └── api/                 # REST API tests
│   │           ├── test_health.py
│   │           ├── test_auth_api.py
│   │           ├── test_companies_api.py
│   │           └── test_insights_api.py
│   │
│   ├── agent-tests/                 # Jest unit + integration tests
│   │   ├── graph-structure.test.js
│   │   ├── node-unit.test.js
│   │   ├── state-transitions.test.js
│   │   ├── error-handling.test.js
│   │   ├── full-workflow.test.js
│   │   └── jest.config.js
│   │
│   ├── langsmith-evals/            # LLM eval suite
│   │   ├── create_dataset.py        # Dataset creation
│   │   ├── evaluators/              # Evaluation functions
│   │   │   ├── insight_length.py
│   │   │   ├── safety_check.py
│   │   │   ├── format_check.py
│   │   │   ├── no_hallucination.py
│   │   │   └── professional_tone.py
│   │   ├── run_evals.py             # Eval runner + reporter
│   │   └── red_team.py              # Security testing
│   │
│   ├── conftest.py                  # Pytest fixtures + setup
│   ├── pytest.ini
│   ├── requirements.txt
│   └── package.json
│
├── .github/
│   └── workflows/
│       └── ci.yml                   # GitHub Actions pipeline
│
├── docs/
│   ├── BUGS.md                      # Intentional bug catalog
│   ├── QA_STRATEGY.md               # Interview reference
│   └── LANGSMITH_GUIDE.md           # LangSmith usage
│
├── package.json                     # Root workspace config
├── .gitignore
├── README.md                        # This file
└── VERSION                          # 1.0.0
```

## Known Issues (Intentional Bugs)

These bugs are **intentionally built in** to demonstrate QA expertise. Tests are written to catch them.

### BUG-001: Case-Sensitive Search
**Location**: `app/src/index.js:82`
- **Severity**: Medium
- **Expected**: Search should be case-insensitive
- **Actual**: Only matches exact case (e.g., "TechCorp" matches, "techcorp" doesn't)
- **Test**: `test_search.py::test_search_case_sensitivity_bug()`
- **Fix**: Use `.toLowerCase()` on both sides of comparison

### BUG-002: Invalid DUNS Returns 200
**Location**: `app/src/index.js:109`
- **Severity**: High (bad API contract)
- **Expected**: GET `/companies/999999999/credit-score` returns 404
- **Actual**: Returns 200 with null/empty data
- **Test**: `test_companies_api.py::test_get_invalid_duns_returns_404()`
- **Fix**: Add `if (!company) return res.status(404).json(...)`

### BUG-003: No Input Validation on Insights
**Location**: `app/src/index.js:118`
- **Severity**: Medium
- **Expected**: POST `/companies/:dunsNumber/insights` requires valid body
- **Actual**: Accepts empty body without validation
- **Test**: `test_insights_api.py::test_insights_no_validation_bug()`
- **Fix**: Add `if (!req.body.dunsNumber) return res.status(400).json(...)`

### BUG-004: Aggressive Rate Limiter
**Location**: `app/src/index.js:18`
- **Severity**: Low (operational issue)
- **Expected**: 10-15 requests per minute is reasonable
- **Actual**: Limited to 3 requests per minute
- **Impact**: Legitimate testing becomes tedious
- **Fix**: Increase `max: 3` to `max: 30`

**See [BUGS.md](./BUGS.md) for detailed reproduction steps and suggested fixes.**

## CI/CD Pipeline

### GitHub Actions Workflow

The `.github/workflows/ci.yml` defines an automated testing pipeline with 7 jobs:

1. **lint** (no dependencies)
   - Runs ESLint on all JavaScript code
   - Flags style violations and unsafe patterns

2. **app-health-check** (depends on: lint)
   - Starts Express app
   - Confirms `/health` endpoint returns 200

3. **api-tests** (depends on: app-health-check)
   - Runs Playwright API tests
   - Validates all REST endpoints

4. **ui-tests** (depends on: api-tests)
   - Runs Playwright UI tests (Chromium only on CI)
   - Validates browser workflows
   - Uploads HTML report on failure

5. **agent-unit-tests** (depends on: lint)
   - Runs Jest tests with mocked dependencies
   - No app server needed

6. **agent-integration-tests** (depends on: api-tests, agent-unit-tests)
   - Runs Jest tests with real API calls
   - Requires ANTHROPIC_API_KEY, LANGCHAIN_API_KEY

7. **langsmith-evals** (depends on: agent-integration-tests, only on push to main)
   - Creates LangSmith dataset
   - Runs evaluation suite
   - Runs red team security tests
   - **Fails build if safety checks fail**

### Setting Up GitHub Secrets

Go to **Settings > Secrets and variables > Actions** and add:

```
ANTHROPIC_API_KEY     = sk-ant-xxxxxxxxxxxx
LANGCHAIN_API_KEY     = sk-xxxxxxxxxxxx
LANGCHAIN_PROJECT     = ai-platform-qa-ci
```

## LangSmith Integration

### What LangSmith Provides

1. **Tracing**: Every agent run is traced and visible in the LangSmith dashboard
2. **Datasets**: Create example inputs with expected outputs for evaluation
3. **Evaluators**: Run custom evaluation functions against agent output
4. **Comparisons**: Compare output quality across model versions or settings
5. **Alerts**: Set thresholds for eval metrics and alert on regressions

### How to Use LangSmith

#### 1. View Traces
- Go to https://smith.langchain.com
- Navigate to your project ("ai-platform-qa")
- Click on any run to see:
  - Full conversation history
  - Latency per step
  - Token usage
  - Output and inputs

#### 2. Create a Dataset

```bash
python tests/langsmith-evals/create_dataset.py
```

This creates a dataset with 6 company examples for evaluation.

#### 3. Run Evals Locally

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
----
000000001    1.0      1.0      1.0      5.0    1.0
000000002    1.0      1.0      1.0      4.0    1.0
...

SUMMARY
================================================================================
Average Professional Tone Score: 4.33/5.0

✓ All safety checks passed
✓ All eval suites passed!
```

#### 4. Red Team Testing

```bash
python tests/langsmith-evals/red_team.py
```

Tests for:
- Prompt injection attacks
- Role override (giving financial advice when it shouldn't)
- PII extraction/fabrication
- Scope creep (doing things outside defined responsibility)

#### 5. Monitor Eval Regressions

In the LangSmith dashboard, set up thresholds:
- Safety check score < 1.0 → Alert
- Professional tone < 3.0 → Alert
- Hallucination detected → Alert

See [LANGSMITH_GUIDE.md](./LANGSMITH_GUIDE.md) for detailed instructions.

## Interview Preparation Guide

This project demonstrates expertise in:

### ✅ Automation Framework Design
- Multi-layer testing strategy (UI, API, Agent, LLM Evals)
- Page Object Model pattern
- Fixture management and setup/teardown
- Async test handling

### ✅ Playwright Expertise
- Browser automation with Python
- Element locators and waits
- Screenshot/video capture on failure
- Multi-browser testing

### ✅ API Testing
- REST endpoint validation
- JWT authentication
- Error handling and status codes
- Response schema validation
- Performance assertions

### ✅ LangGraph / LLM Agent Testing
- Graph structure validation
- Node-level unit testing
- State transition verification
- Error path coverage
- Integration with external APIs

### ✅ LLM Output Evaluation
- LangSmith integration
- Custom evaluation functions
- Hallucination detection
- Safety/compliance checking
- Professional tone assessment

### ✅ CI/CD & DevOps
- GitHub Actions workflows
- Job dependencies and parallelization
- Secret management
- Artifact collection
- Status reporting

### ✅ Production Quality Thinking
- Intentional bugs (real-world QA mindset)
- Comprehensive documentation
- Error handling and edge cases
- Performance monitoring
- Security considerations (red team)

See [QA_STRATEGY.md](./QA_STRATEGY.md) for more details.

## Contributing

When adding tests:

1. Follow the existing file naming convention: `test_*.py` or `*.test.js`
2. Use descriptive test names: `test_<feature>_<expected_outcome>`
3. Add docstrings explaining the test purpose
4. Mark slow tests: `@pytest.mark.slow`
5. Use appropriate fixtures from `conftest.py`

## Troubleshooting

### "App server failed to start"
```bash
# Check if port 3000 is in use
lsof -i :3000

# Kill any process on port 3000
kill -9 <PID>

# Or change PORT in .env
PORT=3001 npm start
```

### "Playwright: browser not found"
```bash
# Reinstall browsers
playwright install
```

### "ANTHROPIC_API_KEY not found"
```bash
# Verify .env file exists and has your key
cat app/.env | grep ANTHROPIC_API_KEY

# Check it's exported
export ANTHROPIC_API_KEY=sk-ant-xxxx
```

### "LangSmith connection failed"
```bash
# Verify your API key is correct
echo $LANGCHAIN_API_KEY

# Check network access to smith.langchain.com
curl -I https://smith.langchain.com
```

### Tests timeout or hang
- Increase timeout: `pytest -o timeout=60 tests/`
- Check if app servers are running
- Review test logs for stuck processes

## Resources

- [Playwright Python Documentation](https://playwright.dev/python/)
- [Pytest Documentation](https://docs.pytest.org/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Anthropic Claude API](https://console.anthropic.com/)

## License

MIT

---

**Built with ❤️ for Dun & Bradstreet Interview Preparation**

Last Updated: April 2024
