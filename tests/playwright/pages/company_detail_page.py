from playwright.async_api import Page


class CompanyDetailPage:
    def __init__(self, page: Page):
        self.page = page

    async def is_open(self) -> bool:
        """Check if detail panel is open."""
        panel = self.page.locator("#detailPanel")
        return await panel.get_attribute("class") == "detail-panel open"

    async def get_company_name(self) -> str:
        """Get company name from detail panel."""
        return await self.page.locator("#detailName").text_content()

    async def get_risk_level(self) -> str:
        """Get risk level from detail panel."""
        return await self.page.locator("#detailRiskLevel").text_content()

    async def get_credit_score(self) -> str:
        """Get credit score from detail panel."""
        return await self.page.locator("#detailCreditScore").text_content()

    async def get_duns_number(self) -> str:
        """Get DUNS number from detail panel."""
        return await self.page.locator("#detailDuns").text_content()

    async def get_industry(self) -> str:
        """Get industry from detail panel."""
        return await self.page.locator("#detailIndustry").text_content()

    async def get_all_fields(self) -> dict:
        """Get all company detail fields."""
        return {
            "name": await self.get_company_name(),
            "duns": await self.get_duns_number(),
            "industry": await self.get_industry(),
            "risk_level": await self.get_risk_level(),
            "credit_score": await self.get_credit_score(),
        }

    async def click_generate_insight(self):
        """Click Generate AI Insight button."""
        await self.page.click("#generateInsightBtn")

    async def get_insight_text(self) -> str:
        """Get the insight text."""
        insight_card = self.page.locator("#insightCard")
        await insight_card.wait_for(state="visible", timeout=20000)
        text = await self.page.locator("#insightText").text_content()
        return text

    async def is_insight_loading(self) -> bool:
        """Check if insight is loading."""
        loading = self.page.locator("#insightLoading")
        return await loading.is_visible()

    async def get_insight_error(self) -> str:
        """Get insight error message if any."""
        error = self.page.locator("#insightError")
        if await error.is_visible():
            return await error.text_content()
        return None

    async def close(self):
        """Close the detail panel."""
        await self.page.click("#closeDetailBtn")
