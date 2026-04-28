import pytest
import asyncio
import subprocess
import time
import requests
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def start_app_server():
    """Start the Express app server before tests."""
    app_dir = PROJECT_ROOT / "app"

    # Start the app server
    app_process = subprocess.Popen(
        ["npm", "start"],
        cwd=str(app_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for app to be ready
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get("http://localhost:3000/health", timeout=2)
            if response.status_code == 200:
                print("\n✓ App server is ready")
                break
        except requests.exceptions.RequestException:
            if i < max_retries - 1:
                time.sleep(1)
            else:
                raise RuntimeError("App server failed to start")

    yield

    # Cleanup
    app_process.terminate()
    try:
        app_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        app_process.kill()


@pytest.fixture(scope="session")
def base_url():
    """Return the base URL for the app."""
    return "http://localhost:3000"


@pytest.fixture
def auth_token():
    """Get a valid JWT token for testing."""
    response = requests.post(
        "http://localhost:3000/auth/login",
        json={"username": "qa_user", "password": "test123"}
    )
    if response.status_code == 200:
        return response.json()["token"]
    raise RuntimeError("Failed to get auth token")
