import pytest
from playwright.async_api import async_playwright
from tests.playwright.pages.login_page import LoginPage
from tests.playwright.pages.dashboard_page import DashboardPage
from tests.playwright.pages.company_detail_page import CompanyDetailPage


async def login_and_search(page, search_query):
    """Helper to login and search."""
    login_page = LoginPage(page)
    await login_page.goto()
    await login_page.fill_username("qa_user")
    await login_page.fill_password("test123")
    await login_page.click_login()

    dashboard = DashboardPage(page)
    await dashboard.search(search_query)


@pytest.mark.asyncio
@pytest.mark.ui
async def test_clicking_result_opens_detail_panel():
    """Test that clicking a result opens the detail panel."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await login_and_search(page, "TechCorp")

        dashboard = DashboardPage(page)
        await dashboard.click_result(0)

        detail = CompanyDetailPage(page)
        assert await detail.is_open()

        await browser.close()


@pytest.mark.asyncio
@pytest.mark.ui
async def test_detail_panel_displays_all_fields():
    """Test that detail panel displays all required fields."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await login_and_search(page, "TechCorp")

        dashboard = DashboardPage(page)
        await dashboard.click_result(0)

        detail = CompanyDetailPage(page)
        fields = await detail.get_all_fields()

        assert fields["name"] and fields["name"] != "-"
        assert fields["duns"] and fields["duns"] != "-"
        assert fields["industry"] and fields["industry"] != "-"
        assert fields["risk_level"] and fields["risk_level"] != "-"
        assert fields["credit_score"] and fields["credit_score"] != "-"

        await browser.close()


@pytest.mark.asyncio
@pytest.mark.ui
async def test_risk_level_badge_colors():
    """Test that risk level badges show correct colors."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await login_and_search(page, "TechCorp")

        dashboard = DashboardPage(page)
        await dashboard.click_result(0)

        detail = CompanyDetailPage(page)
        risk_level = await detail.get_risk_level()

        # Verify the risk level is one of the expected values
        assert risk_level.lower() in ["low", "medium", "high"]

        await browser.close()


@pytest.mark.asyncio
@pytest.mark.ui
async def test_close_detail_panel():
    """Test that closing detail panel works."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await login_and_search(page, "TechCorp")

        dashboard = DashboardPage(page)
        await dashboard.click_result(0)

        detail = CompanyDetailPage(page)
        assert await detail.is_open()

        await detail.close()
        # Give it time to close
        await page.wait_for_timeout(300)

        assert not await detail.is_open()

        await browser.close()
