import pytest
import requests
import jwt


@pytest.mark.api
def test_login_with_valid_credentials(base_url):
    """Test login with valid credentials returns 200 and token."""
    response = requests.post(
        f"{base_url}/auth/login",
        json={"username": "qa_user", "password": "test123"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["token"]


@pytest.mark.api
def test_login_with_invalid_credentials(base_url):
    """Test login with invalid credentials returns 401."""
    response = requests.post(
        f"{base_url}/auth/login",
        json={"username": "wrong_user", "password": "wrong_pass"}
    )

    assert response.status_code == 401
    data = response.json()
    assert "error" in data


@pytest.mark.api
def test_jwt_token_has_valid_format(base_url):
    """Test that returned JWT token has valid format."""
    response = requests.post(
        f"{base_url}/auth/login",
        json={"username": "qa_user", "password": "test123"}
    )

    token = response.json()["token"]

    # JWT should have 3 parts separated by dots
    parts = token.split(".")
    assert len(parts) == 3, f"JWT should have 3 parts, got {len(parts)}"

    # Should be decodable
    decoded = jwt.decode(token, options={"verify_signature": False})
    assert "username" in decoded
    assert decoded["username"] == "qa_user"


@pytest.mark.api
def test_login_missing_username(base_url):
    """Test login with missing username returns error."""
    response = requests.post(
        f"{base_url}/auth/login",
        json={"password": "test123"}
    )

    assert response.status_code == 401


@pytest.mark.api
def test_login_missing_password(base_url):
    """Test login with missing password returns error."""
    response = requests.post(
        f"{base_url}/auth/login",
        json={"username": "qa_user"}
    )

    assert response.status_code == 401
