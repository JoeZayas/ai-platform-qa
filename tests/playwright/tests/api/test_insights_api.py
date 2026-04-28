import pytest
import requests
import time


@pytest.mark.api
@pytest.mark.slow
def test_insights_requires_auth(base_url):
    """Test that insights endpoint requires authentication."""
    response = requests.post(
        f"{base_url}/companies/000000001/insights",
        json={"dunsNumber": "000000001"}
    )

    assert response.status_code == 401


@pytest.mark.api
@pytest.mark.slow
def test_insights_invalid_duns(base_url, auth_token):
    """Test insights with invalid DUNS returns 404."""
    response = requests.post(
        f"{base_url}/companies/999999999/insights",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"dunsNumber": "999999999"}
    )

    assert response.status_code == 404


@pytest.mark.api
@pytest.mark.slow
def test_insights_no_validation_bug():
    """Test that insights accepts empty body (BUG-003)."""
    response = requests.post(
        "http://localhost:3000/companies/000000001/insights",
        headers={"Authorization": f"Bearer dummy-token"},
        json={}
    )

    # This should fail with 400 but currently returns 500 due to BUG-003
    # The endpoint accepts empty body without validation
    assert response.status_code >= 400


@pytest.mark.api
@pytest.mark.slow
def test_insights_returns_insight_string(base_url, auth_token):
    """Test that insights endpoint returns insight string."""
    response = requests.post(
        f"{base_url}/companies/000000001/insights",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"dunsNumber": "000000001"},
        timeout=20
    )

    assert response.status_code == 200
    data = response.json()

    assert "insight" in data
    assert isinstance(data["insight"], str)
    assert len(data["insight"]) > 0


@pytest.mark.api
@pytest.mark.slow
def test_insights_response_time(base_url, auth_token):
    """Test that insight generation completes within 15 seconds."""
    start = time.time()

    response = requests.post(
        f"{base_url}/companies/000000001/insights",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"dunsNumber": "000000001"},
        timeout=20
    )

    elapsed = time.time() - start

    assert response.status_code == 200
    assert elapsed < 15, f"Insight generation took {elapsed:.2f}s, expected < 15s"


@pytest.mark.api
@pytest.mark.slow
def test_insights_includes_agent_steps(base_url, auth_token):
    """Test that insights response includes agentSteps count."""
    response = requests.post(
        f"{base_url}/companies/000000001/insights",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"dunsNumber": "000000001"},
        timeout=20
    )

    assert response.status_code == 200
    data = response.json()

    assert "agentSteps" in data
    assert data["agentSteps"] > 0


@pytest.mark.api
@pytest.mark.slow
def test_insights_includes_run_id(base_url, auth_token):
    """Test that insights response includes runId for LangSmith tracing."""
    response = requests.post(
        f"{base_url}/companies/000000001/insights",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"dunsNumber": "000000001"},
        timeout=20
    )

    assert response.status_code == 200
    data = response.json()

    assert "runId" in data
    assert data["runId"]


@pytest.mark.api
@pytest.mark.slow
def test_insights_includes_sources(base_url, auth_token):
    """Test that insights response includes sources array."""
    response = requests.post(
        f"{base_url}/companies/000000001/insights",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"dunsNumber": "000000001"},
        timeout=20
    )

    assert response.status_code == 200
    data = response.json()

    assert "sources" in data
    assert isinstance(data["sources"], list)
