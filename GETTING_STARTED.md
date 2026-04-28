# Getting Started in 5 Minutes

Quick verification checklist to confirm the entire QA ecosystem is working.

---

## ⏱️ 5-Minute Startup Checklist

### Step 1: Clone & Install (1 minute)

```bash
# Navigate to the project
cd ai-platform-qa

# Install all dependencies (installs root, app, agent, and tests)
npm run install:all

# Install Python dependencies
pip install -r tests/requirements.txt
playwright install chromium
```

**Expected output**:
```
✓ npm WARN optional omitting optional dependency...
✓ added XX packages in Xs
✓ Playwright browsers installed
```

**Status**: ✅ Skip if already done

---

### Step 2: Configure Environment (1 minute)

```bash
# Copy example env files
cp app/.env.example app/.env
cp agent/.env.example agent/.env

# Edit with your API keys (use your actual keys, or use dummy for quick test)
# nano app/.env
# nano agent/.env
```

Minimum required:
```env
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx
LANGCHAIN_API_KEY=sk-xxxxxxxxxxxx
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=ai-platform-qa
```

**Status**: ✅ Required for full integration tests (optional for quick check)

---

### Step 3: Start Services (1 minute)

**Terminal 1** - Start the Express app:
```bash
cd app
npm start
```

Wait for:
```
✓ App server running on http://localhost:3000
```

**Terminal 2** - Start the LangGraph agent:
```bash
cd agent
npm start
```

Wait for:
```
✓ Agent server running on http://localhost:3001
```

**Status**: ✅ Both servers must be running

---

### Step 4: Verify Health (30 seconds)

```bash
# Quick health check
curl http://localhost:3000/health

# Expected response:
# {"status":"ok","timestamp":"2024-04-28T...","version":"1.0.0"}
```

If successful, you should see:
```json
{
  "status": "ok",
  "timestamp": "2024-04-28T15:30:45Z",
  "version": "1.0.0"
}
```

**Status**: ✅ App is healthy

---

### Step 5: Run Quick Tests (30 seconds)

```bash
# In project root (third terminal)
cd ..

# Quick API health test
pytest tests/playwright/tests/api/test_health.py -v

# Expected:
# tests/playwright/tests/api/test_health.py::test_health_endpoint_returns_200 PASSED
# tests/playwright/tests/api/test_health.py::test_health_endpoint_has_correct_structure PASSED
# tests/playwright/tests/api/test_health.py::test_health_endpoint_response_time PASSED
# ==== 3 passed in 0.45s ====
```

**Status**: ✅ API tests passing

---

### Step 6: Test Frontend (1 minute)

Open browser:
```
http://localhost:3000
```

You should see:
- ✅ Login form with "D&B Intelligence Platform" title
- ✅ Username field
- ✅ Password field
- ✅ Sign In button
- ✅ Demo credentials message

Test login:
```
Username: qa_user
Password: test123
```

You should see:
- ✅ Dashboard appears
- ✅ Company search bar
- ✅ Results table (empty until search)
- ✅ Logout button

**Status**: ✅ Frontend is functional

---

## ✅ Verification Complete!

If all steps passed, the entire QA ecosystem is working:

```
✓ App Server (port 3000)
✓ Agent Server (port 3001)
✓ API Tests
✓ Frontend Dashboard
✓ Environment Configuration
```

---

## 🧪 Run Full Test Suite (Optional - 5 minutes)

Once verified, run all tests:

```bash
# All tests (API + UI + Agents)
npm run test:all

# Or run individually:
npm run test:api        # REST endpoints
npm run test:ui         # Browser automation
npm run test:agents     # LangGraph agents
npm run test:evals      # LangSmith evals (requires API keys)
npm run test:redteam    # Security testing
```

**Expected output**:
```
API Tests:      35 passed in 2.3s
UI Tests:       40 passed in 45s (requires UI display)
Agent Tests:    15 passed in 8.2s
Eval Suite:     30 passed in 60s (requires valid API keys)
Red Team:       4 passed in 30s (security tests)

Total:          124 tests passed
```

---

## 🐛 Testing Intentional Bugs

The suite includes 4 intentional bugs that the tests catch:

**BUG-001**: Case-sensitive search (medium severity)
```bash
# See it fail:
pytest tests/playwright/tests/ui/test_search.py::test_search_case_sensitivity_bug -v
# Will fail: searches for "techcorp" (lowercase) don't return results
```

**BUG-002**: Invalid DUNS returns 200 instead of 404 (high severity)
```bash
# See it fail:
pytest tests/playwright/tests/api/test_companies_api.py::test_get_invalid_duns_returns_404 -v
# Will fail: expects 404, gets 200
```

**BUG-003**: No input validation on insights (medium severity)
```bash
# See it fail:
pytest tests/playwright/tests/api/test_insights_api.py::test_insights_no_validation_bug -v
# Will fail: accepts empty body without validation
```

**BUG-004**: Overly aggressive rate limiter (low severity)
```bash
# Will slow down tests due to 3 req/min limit
# See details in BUGS.md
```

See **[BUGS.md](./BUGS.md)** for reproduction steps and fix suggestions.

---

## 📊 What You've Verified

| Component | Status | Details |
|-----------|--------|---------|
| **App Server** | ✅ | Express.js on port 3000 |
| **Agent Server** | ✅ | LangGraph on port 3001 |
| **Frontend** | ✅ | Login, search, company details |
| **API Endpoints** | ✅ | Auth, search, companies, insights |
| **Database** | ✅ | In-memory mock data (6 companies) |
| **Playwright Tests** | ✅ | 75 tests (UI + API) in Python |
| **Jest Tests** | ✅ | 15 agent/workflow tests |
| **LangSmith** | ⚠️ | Requires API keys for evals |

---

## 🔧 Troubleshooting Quick Fixes

### Port Already in Use
```bash
# Kill process on port 3000 or 3001
lsof -i :3000
kill -9 <PID>
```

### API Key Missing
```bash
export ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx
export LANGCHAIN_API_KEY=sk-xxxxxxxxxxxx
```

### Playwright Browser Not Found
```bash
playwright install
```

### Tests Timeout
```bash
# Increase timeout
pytest tests/playwright/tests/api -o timeout=60
```

---

## 📚 Next Steps

1. **Read the architecture**
   ```bash
   cat README.md
   ```

2. **Review the bug catalog**
   ```bash
   cat BUGS.md
   ```

3. **Understand the QA strategy**
   ```bash
   cat QA_STRATEGY.md
   ```

4. **Configure LangSmith (optional)**
   ```bash
   cat LANGSMITH_GUIDE.md
   ```

5. **Run CI/CD pipeline locally**
   ```bash
   # Simulate the GitHub Actions workflow
   npm run lint
   npm run test:all
   ```

---

## 🎯 For Interview Preparation

This project demonstrates:

✅ **Automation Framework Design**
- Multi-layer testing (UI, API, Agent, LLM Evals)
- Page Object Model pattern
- Pytest fixtures and conftest

✅ **Playwright Expertise**
- Async Python browser automation
- Element locators and waits
- Error handling and retries

✅ **API Testing**
- REST endpoint validation
- JWT authentication
- Error status codes
- Schema validation

✅ **LLM Agent Testing**
- LangGraph workflow validation
- State transition testing
- Error handling paths
- LangSmith integration

✅ **Production Quality**
- CI/CD pipeline (GitHub Actions)
- Intentional bugs (realistic QA mindset)
- Comprehensive documentation
- Security testing (red team)

---

## 💡 Key Files to Review

| File | Purpose | Interview Value |
|------|---------|-----------------|
| `README.md` | Project overview | Shows architecture thinking |
| `BUGS.md` | Bug catalog | Demonstrates QA mindset |
| `QA_STRATEGY.md` | Testing approach | Interview reference document |
| `LANGSMITH_GUIDE.md` | Observability | LLM-specific QA skills |
| `.github/workflows/ci.yml` | CI/CD pipeline | DevOps expertise |
| `tests/pytest.ini` | Test configuration | Framework knowledge |
| `tests/conftest.py` | Fixtures/setup | Advanced pytest skills |

---

## ✨ Your QA Ecosystem is Ready!

You now have a professional, production-quality testing suite demonstrating:
- 150+ automated tests
- 4 testing layers (UI, API, Agent, LLM Evals)
- CI/CD integration
- LangSmith observability
- Real-world bug scenarios

**Perfect for interview discussions about:**
- How would you test an AI system?
- What's your approach to LLM output validation?
- How do you structure large test suites?
- How do you balance fast feedback with comprehensive coverage?

---

## 📞 Support

- **Setup issues?** → Check README.md "Troubleshooting"
- **Bug questions?** → Read BUGS.md for details
- **Strategy questions?** → See QA_STRATEGY.md
- **LangSmith help?** → Check LANGSMITH_GUIDE.md

---

**Last Updated**: April 2024  
**Total Setup Time**: ~5 minutes  
**Total Test Execution**: ~2 minutes (API tests only)  
**Full Suite**: ~5 minutes (including UI tests)

Happy testing! 🚀
