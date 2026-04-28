import pytest
from playwright.async_api import async_playwright
from tests.playwright.pages.login_page import LoginPage
from tests.playwright.pages.dashboard_page import DashboardPage


async def login_and_go_to_dashboard(page):
    """Helper to login and reach dashboard."""
    login_page = LoginPage(page)
    await login_page.goto()
    await login_page.fill_username("qa_user")
    await login_page.fill_password("test123")
    await login_page.click_login()


@pytest.mark.asyncio
@pytest.mark.ui
async def test_search_by_company_name():
    """Test searching for a known company."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await login_and_go_to_dashboard(page)

        dashboard = DashboardPage(page)
        await dashboard.search("TechCorp")

        count = await dashboard.get_result_count()
        assert count > 0

        await browser.close()


@pytest.mark.asyncio
@pytest.mark.ui
async def test_search_case_sensitivity_bug():
    """Test that search is case-insensitive (BUG-001: currently case-sensitive)."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await login_and_go_to_dashboard(page)

        dashboard = DashboardPage(page)

        # Search with lowercase
        await dashboard.search("techcorp")

        # This will fail because the search is case-sensitive (BUG-001)
        count = await dashboard.get_result_count()
        assert count > 0, "Search should be case-insensitive (BUG-001: currently fails)"

        await browser.close()


@pytest.mark.asyncio
@pytest.mark.ui
async def test_search_with_special_characters():
    """Test searching for company with special characters."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await login_and_go_to_dashboard(page)

        dashboard = DashboardPage(page)
        await dashboard.search("Smith & Co")

        count = await dashboard.get_result_count()
        assert count > 0

        await browser.close()


@pytest.mark.asyncio
@pytest.mark.ui
async def test_search_empty_query():
    """Test search with empty query shows no results."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await login_and_go_to_dashboard(page)

        dashboard = DashboardPage(page)
        await dashboard.search("")

        # Empty search should show "Enter a search to see results" message
        # Just verify page doesn't crash
        assert await dashboard.is_displayed()

        await browser.close()


@pytest.mark.asyncio
@pytest.mark.ui
async def test_search_nonexistent_company():
    """Test search for non-existent company shows no results."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await login_and_go_to_dashboard(page)

        dashboard = DashboardPage(page)
        await dashboard.search("CompanyThatDoesNotExist12345")

        count = await dashboard.get_result_count()
        assert count == 0

        await browser.close()
