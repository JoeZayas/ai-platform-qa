from playwright.async_api import Page


class DashboardPage:
    def __init__(self, page: Page):
        self.page = page

    async def is_displayed(self) -> bool:
        """Check if dashboard is displayed."""
        return await self.page.locator("#dashboardScreen").is_visible()

    async def search(self, query: str):
        """Perform a search."""
        await self.page.fill("#searchInput", query)
        await self.page.click("#searchBtn")
        # Wait for results to load
        await self.page.wait_for_selector(".results-table tbody tr", timeout=5000)

    async def get_result_rows(self) -> list:
        """Get all result rows."""
        rows = await self.page.locator(".results-table tbody tr").all()
        return rows

    async def get_result_count(self) -> int:
        """Get number of result rows."""
        rows = await self.get_result_rows()
        # Filter out "no results" message row
        count = 0
        for row in rows:
            cells = await row.locator("td").all()
            if len(cells) == 4:  # Valid result row
                count += 1
        return count

    async def click_result(self, index: int):
        """Click on a result row."""
        rows = await self.get_result_rows()
        if index < len(rows):
            await rows[index].click()

    async def logout(self):
        """Click logout button."""
        await self.page.click("#logoutBtn")
