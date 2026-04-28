from playwright.async_api import Page


class LoginPage:
    def __init__(self, page: Page):
        self.page = page

    async def goto(self):
        """Navigate to login page."""
        await self.page.goto("http://localhost:3000")

    async def fill_username(self, username: str):
        """Enter username."""
        await self.page.fill("#username", username)

    async def fill_password(self, password: str):
        """Enter password."""
        await self.page.fill("#password", password)

    async def click_login(self):
        """Click login button."""
        await self.page.click("button[type='submit']")

    async def get_error_message(self) -> str:
        """Get error message text."""
        error_div = self.page.locator("#loginError")
        await error_div.wait_for(state="visible", timeout=5000)
        return await error_div.text_content()

    async def is_error_visible(self) -> bool:
        """Check if error message is visible."""
        error_div = self.page.locator("#loginError")
        return await error_div.is_visible()
