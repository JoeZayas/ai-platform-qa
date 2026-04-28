# Intentional Bugs Catalog

This document catalogs the intentional bugs built into the platform to demonstrate QA expertise. These bugs are discovered and caught by the automated test suite.

---

## BUG-001: Case-Sensitive Search

**Bug ID**: BUG-001  
**Status**: Unresolved (intentional)  
**Severity**: Medium  
**Component**: Company Search API  
**Affected Endpoint**: `GET /companies/search?q={query}`

### Expected Behavior
The search endpoint should perform **case-insensitive** matching on company names and industries.

Example:
- Query: `techcorp` → Should return TechCorp Global Inc.
- Query: `TECHCORP` → Should return TechCorp Global Inc.
- Query: `TechCorp` → Should return TechCorp Global Inc.

### Actual Behavior
The search endpoint performs **case-sensitive** matching.

Example:
- Query: `TechCorp` → Returns TechCorp Global Inc. ✓
- Query: `techcorp` → Returns empty array ✗
- Query: `TECHCORP` → Returns empty array ✗

### Root Cause
**File**: `app/src/index.js`, **Line**: 82

```javascript
// Current (WRONG):
const results = companies.filter(company =>
  company.name.includes(q) ||
  company.industry.includes(q)
);

// Should be:
const results = companies.filter(company =>
  company.name.toLowerCase().includes(q.toLowerCase()) ||
  company.industry.toLowerCase().includes(q.toLowerCase())
);
```

### Test That Catches It
**File**: `tests/playwright/tests/ui/test_search.py`  
**Test Name**: `test_search_case_sensitivity_bug()`

```python
async def test_search_case_sensitivity_bug():
    """Test that search is case-insensitive (BUG-001: currently case-sensitive)."""
    # Searches for "techcorp" in lowercase
    # Expects results, but gets empty due to case sensitivity
    assert count > 0, "Search should be case-insensitive (BUG-001: currently fails)"
```

### Steps to Reproduce
1. Log in to the dashboard
2. Search for "techcorp" (lowercase)
3. Expected: Results show "TechCorp Global Inc."
4. Actual: "No results found"

### Impact
- Users cannot find companies using lowercase search
- Breaks accessibility for users who don't capitalize properly
- Test count: 1 test fails

### Suggested Fix
Update both the UI and API search logic to normalize case:
1. Convert `q` to lowercase
2. Convert company.name and company.industry to lowercase
3. Perform comparison
4. Return original company objects (not lowercased)

**Difficulty**: Easy | **Time**: 5 minutes

---

## BUG-002: Invalid DUNS Returns 200 Instead of 404

**Bug ID**: BUG-002  
**Status**: Unresolved (intentional)  
**Severity**: High  
**Component**: Credit Score API  
**Affected Endpoint**: `GET /companies/:dunsNumber/credit-score`

### Expected Behavior
When requesting credit score for a non-existent DUNS number, the API should return **404 Not Found** with an error message.

### Actual Behavior
The API returns **200 OK** with null/empty data, breaking the HTTP contract and making error handling difficult for clients.

```
GET /companies/999999999/credit-score
Content-Type: application/json

Response (200):
{
  "creditScore": null,
  "riskLevel": null
}
```

### Root Cause
**File**: `app/src/index.js`, **Lines**: 109-111

```javascript
// Current (WRONG):
if (!company) {
  // BUG-002: Should return 404, but returns 200 with empty data
  return res.json({ creditScore: null, riskLevel: null });
}

// Should be:
if (!company) {
  return res.status(404).json({ error: 'Company not found' });
}
```

### Test That Catches It
**File**: `tests/playwright/tests/api/test_companies_api.py`  
**Test Name**: `test_get_invalid_duns_returns_404()`

```python
def test_get_invalid_duns_returns_404(base_url, auth_token):
    """Test that invalid DUNS returns 404."""
    response = requests.get(
        f"{base_url}/companies/999999999/credit-score",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 404  # FAILS - gets 200
```

### Steps to Reproduce
1. Authenticate with valid credentials (get JWT token)
2. Make request:
   ```bash
   curl -H "Authorization: Bearer <token>" \
     http://localhost:3000/companies/999999999/credit-score
   ```
3. Expected: HTTP 404
4. Actual: HTTP 200 with empty data

### Impact
- **API Contract Violation**: Clients can't distinguish between success and failure
- **Poor Error Handling**: Clients must check for null values instead of HTTP status
- **Inconsistent Behavior**: Same endpoint returns 404 for company lookup but 200 for credit score
- **Test count**: 1 test fails

### Suggested Fix
Add proper status code handling:

```javascript
if (!company) {
  return res.status(404).json({
    error: 'Company not found',
    dunsNumber: dunsNumber
  });
}
```

**Difficulty**: Very Easy | **Time**: 2 minutes

---

## BUG-003: No Input Validation on Insights Endpoint

**Bug ID**: BUG-003  
**Status**: Unresolved (intentional)  
**Severity**: Medium  
**Component**: Insights Generation API  
**Affected Endpoint**: `POST /companies/:dunsNumber/insights`

### Expected Behavior
The insights endpoint should:
1. Require a valid request body
2. Validate that `dunsNumber` is present
3. Return **400 Bad Request** if validation fails

### Actual Behavior
The endpoint accepts any request body, including:
- Empty object `{}`
- Null values
- Missing required fields

This leads to downstream errors when the agent tries to process invalid data.

### Root Cause
**File**: `app/src/index.js`, **Lines**: 118-120

```javascript
// Current (WRONG):
app.post('/companies/:dunsNumber/insights', verifyToken, async (req, res) => {
  try {
    const { dunsNumber } = req.body;
    // BUG-003: No validation of request body or its fields
    
    const company = companies.find(c => c.dunsNumber === dunsNumber);
    // This can fail silently or cause cryptic errors
```

### Test That Catches It
**File**: `tests/playwright/tests/api/test_insights_api.py`  
**Test Name**: `test_insights_no_validation_bug()`

```python
def test_insights_no_validation_bug():
    """Test that insights accepts empty body (BUG-003)."""
    response = requests.post(
        "http://localhost:3000/companies/000000001/insights",
        headers={"Authorization": f"Bearer dummy-token"},
        json={}
    )
    # Should return 400, but returns 500 or 200
    assert response.status_code == 400
```

### Steps to Reproduce
1. Authenticate with valid credentials
2. Make POST request with empty body:
   ```bash
   curl -X POST \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{}' \
     http://localhost:3000/companies/000000001/insights
   ```
3. Expected: HTTP 400 with "Missing required field: dunsNumber"
4. Actual: HTTP 200 or 500 (unpredictable)

### Impact
- **Unclear Errors**: Client receives confusing error messages
- **Bad Data Processing**: Agent receives undefined values and behaves unpredictably
- **Debugging Difficulty**: Hard to trace where the error originated
- **Test count**: 1 test fails

### Suggested Fix
Add input validation at the start of the endpoint:

```javascript
app.post('/companies/:dunsNumber/insights', verifyToken, async (req, res) => {
  // Validation
  if (!req.body || !req.body.dunsNumber) {
    return res.status(400).json({
      error: 'Missing required field',
      field: 'dunsNumber'
    });
  }

  const { dunsNumber } = req.body;
  // ... rest of code
```

**Difficulty**: Easy | **Time**: 10 minutes

---

## BUG-004: Overly Aggressive Rate Limiter

**Bug ID**: BUG-004  
**Status**: Unresolved (intentional)  
**Severity**: Low  
**Component**: Rate Limiting Middleware  
**Affected Endpoint**: All `/companies/*` endpoints

### Expected Behavior
Rate limiter should allow a reasonable number of requests per minute for legitimate API usage (e.g., 30-60 req/min).

### Actual Behavior
Rate limiter is set to **3 requests per minute**, which is too restrictive for normal testing and legitimate API use.

```javascript
const limiter = rateLimit({
  windowMs: 60 * 1000,  // 1 minute window
  max: 3,               // TOO LOW - only 3 requests!
  message: 'Too many requests from this IP'
});
app.use('/companies/', limiter);
```

### Root Cause
**File**: `app/src/index.js`, **Lines**: 18-23

```javascript
const limiter = rateLimit({
  windowMs: 60 * 1000,
  max: 3,              // BUG-004: Should be 30-60
  message: 'Too many requests from this IP'
});
```

### Impact
- **Testing Friction**: Tests must wait 60+ seconds to continue
- **Poor User Experience**: Legitimate users hit rate limits too quickly
- **Not Production Realistic**: Dun & Bradstreet APIs would allow more requests
- **Operational Issue**: Not a correctness bug, but impacts usability

### Suggested Fix
Increase the limit:

```javascript
const limiter = rateLimit({
  windowMs: 60 * 1000,
  max: 30,  // More reasonable for testing and general use
  message: 'Too many requests from this IP, please try again later'
});
```

Or make it configurable via environment variable:

```javascript
const limiter = rateLimit({
  windowMs: 60 * 1000,
  max: parseInt(process.env.RATE_LIMIT_MAX || 30),
  message: 'Too many requests from this IP, please try again later'
});
```

**Difficulty**: Very Easy | **Time**: 2 minutes

---

## Summary Table

| ID | Component | Severity | Detected By | Status |
|----|-----------|----------|-------------|--------|
| BUG-001 | Search | Medium | UI & API Tests | Found |
| BUG-002 | Credit Score | High | API Tests | Found |
| BUG-003 | Insights | Medium | API Tests | Found |
| BUG-004 | Rate Limiter | Low | Manual Testing | Found |

## Total Test Coverage

- **Tests that fail due to bugs**: 4
- **Tests that pass**: 30+
- **Bug detection rate**: 100%

## Remediation Plan

For the interview, you can discuss:

1. **Bug Discovery Process**
   - How did you identify these bugs?
   - What testing approach caught them?
   - How would you prevent similar issues?

2. **Prioritization**
   - BUG-002 is critical (API contract violation)
   - BUG-001 and BUG-003 are important (functionality issues)
   - BUG-004 is nice-to-have (operational improvement)

3. **Testing Strategy**
   - Unit tests would catch BUG-003
   - API contract tests would catch BUG-002
   - Integration tests would catch BUG-001
   - Load tests would reveal BUG-004

---

See [README.md](./README.md) for more context on the project.
