import pytest
import requests
import time


@pytest.mark.api
def test_health_endpoint_returns_200(base_url):
    """Test that /health endpoint returns 200."""
    response = requests.get(f"{base_url}/health")
    assert response.status_code == 200


@pytest.mark.api
def test_health_endpoint_has_correct_structure(base_url):
    """Test that /health response has correct structure."""
    response = requests.get(f"{base_url}/health")
    data = response.json()

    assert "status" in data
    assert data["status"] == "ok"
    assert "timestamp" in data
    assert "version" in data


@pytest.mark.api
def test_health_endpoint_response_time(base_url):
    """Test that health endpoint responds under 200ms."""
    start = time.time()
    response = requests.get(f"{base_url}/health")
    elapsed = (time.time() - start) * 1000

    assert elapsed < 200, f"Health check took {elapsed:.2f}ms, expected < 200ms"
    assert response.status_code == 200
