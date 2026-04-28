import pytest
import requests


@pytest.mark.api
def test_search_returns_array(base_url):
    """Test that search returns array of company objects."""
    response = requests.get(f"{base_url}/companies/search?q=TechCorp")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.api
def test_search_results_have_required_fields(base_url):
    """Test that search results have required fields."""
    response = requests.get(f"{base_url}/companies/search?q=TechCorp")

    data = response.json()
    assert len(data) > 0

    for company in data:
        assert "dunsNumber" in company
        assert "name" in company
        assert "industry" in company
        assert "riskLevel" in company


@pytest.mark.api
def test_search_case_sensitivity_bug():
    """Test that search is case-sensitive (BUG-001)."""
    response = requests.get("http://localhost:3000/companies/search?q=techcorp")

    # This test expects 0 results due to case sensitivity (BUG-001)
    data = response.json()
    assert len(data) == 0, "BUG-001: Search is case-sensitive and should fail with lowercase"


@pytest.mark.api
def test_search_empty_query(base_url):
    """Test search with empty query returns empty array."""
    response = requests.get(f"{base_url}/companies/search")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


@pytest.mark.api
def test_search_nonexistent_company(base_url):
    """Test search for non-existent company returns empty array."""
    response = requests.get(f"{base_url}/companies/search?q=CompanyThatDoesNotExist")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


@pytest.mark.api
def test_get_company_by_duns_requires_auth(base_url, auth_token):
    """Test that getting company by DUNS requires authentication."""
    response = requests.get(f"{base_url}/companies/000000001")
    assert response.status_code == 401

    # With token should succeed
    response = requests.get(
        f"{base_url}/companies/000000001",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200


@pytest.mark.api
def test_get_company_by_duns_returns_details(base_url, auth_token):
    """Test that getting company by DUNS returns company details."""
    response = requests.get(
        f"{base_url}/companies/000000001",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["dunsNumber"] == "000000001"
    assert data["name"] == "TechCorp Global Inc."


@pytest.mark.api
def test_get_invalid_duns_returns_404(base_url, auth_token):
    """Test that invalid DUNS returns 404."""
    response = requests.get(
        f"{base_url}/companies/999999999",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 404


@pytest.mark.api
def test_search_with_special_characters(base_url):
    """Test search for company with special characters."""
    response = requests.get(f"{base_url}/companies/search?q=Smith & Co")

    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
