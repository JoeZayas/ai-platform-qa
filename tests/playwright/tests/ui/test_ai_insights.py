import pytest
from playwright.async_api import async_playwright
from tests.playwright.pages.login_page import LoginPage
from tests.playwright.pages.dashboard_page import DashboardPage
from tests.playwright.pages.company_detail_page import CompanyDetailPage


async def open_company_detail(page, search_query):
    """Helper to open company detail."""
    login_page = LoginPage(page)
    await login_page.goto()
    await login_page.fill_username("qa_user")
    await login_page.fill_password("test123")
    await login_page.click_login()

    dashboard = DashboardPage(page)
    await dashboard.search(search_query)
    await dashboard.click_result(0)


@pytest.mark.asyncio
@pytest.mark.ui
@pytest.mark.slow
async def test_generate_insight_shows_loading():
    """Test that generating insight shows loading spinner."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await open_company_detail(page, "TechCorp")

        detail = CompanyDetailPage(page)
        await detail.click_generate_insight()

        # Check loading state appears
        assert await detail.is_insight_loading()

        await browser.close()


@pytest.mark.asyncio
@pytest.mark.ui
@pytest.mark.slow
async def test_insight_appears_within_15_seconds():
    """Test that insight text appears within 15 seconds."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await open_company_detail(page, "TechCorp")

        detail = CompanyDetailPage(page)
        await detail.click_generate_insight()

        # Wait for insight (timeout is 15 seconds in get_insight_text)
        insight_text = await detail.get_insight_text()
        assert insight_text

        await browser.close()


@pytest.mark.asyncio
@pytest.mark.ui
@pytest.mark.slow
async def test_insight_is_substantial():
    """Test that insight is non-empty and at least 100 characters."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await open_company_detail(page, "TechCorp")

        detail = CompanyDetailPage(page)
        await detail.click_generate_insight()

        insight_text = await detail.get_insight_text()
        assert len(insight_text) >= 100

        await browser.close()


@pytest.mark.asyncio
@pytest.mark.ui
@pytest.mark.slow
async def test_insight_does_not_contain_error():
    """Test that insight does not contain error messages."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await open_company_detail(page, "TechCorp")

        detail = CompanyDetailPage(page)
        await detail.click_generate_insight()

        insight_text = await detail.get_insight_text()
        error = await detail.get_insight_error()

        assert error is None or error == ""

        await browser.close()


@pytest.mark.asyncio
@pytest.mark.ui
@pytest.mark.slow
async def test_generating_insight_twice_produces_different_results():
    """Test that generating insight twice produces non-identical results (non-determinism)."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await open_company_detail(page, "TechCorp")

        detail = CompanyDetailPage(page)

        # Generate first insight
        await detail.click_generate_insight()
        insight1 = await detail.get_insight_text()

        # Reset and generate again
        await detail.close()
        await page.wait_for_timeout(500)

        dashboard = DashboardPage(page)
        await dashboard.search("TechCorp")
        await dashboard.click_result(0)

        detail2 = CompanyDetailPage(page)
        await detail2.click_generate_insight()
        insight2 = await detail2.get_insight_text()

        # They should be different (non-deterministic LLM output)
        assert insight1 != insight2, "LLM output should vary between calls"

        await browser.close()
