import pytest
from playwright.async_api import async_playwright, expect
from tests.playwright.pages.login_page import LoginPage
from tests.playwright.pages.dashboard_page import DashboardPage


@pytest.mark.asyncio
@pytest.mark.ui
async def test_valid_credentials_show_dashboard():
    """Test that valid credentials display the dashboard."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        login_page = LoginPage(page)
        await login_page.goto()

        await login_page.fill_username("qa_user")
        await login_page.fill_password("test123")
        await login_page.click_login()

        dashboard = DashboardPage(page)
        assert await dashboard.is_displayed()

        await browser.close()


@pytest.mark.asyncio
@pytest.mark.ui
async def test_invalid_credentials_show_error():
    """Test that invalid credentials show error message."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        login_page = LoginPage(page)
        await login_page.goto()

        await login_page.fill_username("wrong_user")
        await login_page.fill_password("wrong_pass")
        await login_page.click_login()

        assert await login_page.is_error_visible()
        error_msg = await login_page.get_error_message()
        assert "Invalid credentials" in error_msg

        await browser.close()


@pytest.mark.asyncio
@pytest.mark.ui
async def test_logout_redirects_to_login():
    """Test that logout redirects to login page."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Login
        login_page = LoginPage(page)
        await login_page.goto()
        await login_page.fill_username("qa_user")
        await login_page.fill_password("test123")
        await login_page.click_login()

        dashboard = DashboardPage(page)
        assert await dashboard.is_displayed()

        # Logout
        await dashboard.logout()
        await page.wait_for_timeout(500)

        # Should be back at login
        assert not await dashboard.is_displayed()

        await browser.close()
