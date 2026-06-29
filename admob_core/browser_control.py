import asyncio
import os
from playwright.async_api import async_playwright

class BrowserControl:
    """
    Lazy-loaded, headless Playwright session manager for AdMob Console operations
    that the REST API doesn't support (like Policy Center).
    """
    def __init__(self, session_dir=".admob_session"):
        self.session_dir = session_dir
        self.playwright = None
        self.browser = None
        self.context = None
        
    async def get_context(self):
        if not os.path.exists(self.session_dir):
            raise Exception("No browser session found! Please run `python -m admob_mcp.login` first to authenticate.")
            
        if self.context:
            return self.context
            
        self.playwright = await async_playwright().start()
        # Headless mode for tools, using the persistent context created by login.py
        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.session_dir,
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        return self.context
        
    async def close(self):
        if self.context:
            await self.context.close()
            self.context = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None

    async def check_session_valid(self, page) -> bool:
        """
        Check if we are logged in by looking for sign-in buttons or URLs.
        """
        url = page.url
        if "ServiceLogin" in url or "accounts.google.com" in url:
            return False
        return True

    async def fetch_policy_issues(self) -> dict:
        """
        Navigates to the AdMob Policy Center and extracts violations.
        """
        context = await self.get_context()
        page = await context.new_page()
        
        try:
            await page.goto("https://apps.admob.com/v2/policycenter")
            # Wait for either policy center content or a login redirect
            await page.wait_for_load_state("networkidle", timeout=15000)
            
            if not await self.check_session_valid(page):
                raise Exception("AdMob browser session expired! Please run `python -m admob_mcp.login` to re-authenticate.")
            
            # This is a stub scraper logic. In a real scenario, you would inspect
            # the DOM elements of the Policy Center to extract table rows.
            # For now, we will extract the visible text to provide a summary.
            
            # Check if there are issues
            page_text = await page.evaluate("document.body.innerText")
            has_issues = "No issues found" not in page_text and "No current issues" not in page_text
            
            # Simple DOM scraping
            issues = []
            if has_issues:
                # We extract the main table or list items of violations.
                # Since AdMob obfuscates classes, grabbing innerText of specific semantic elements is safer.
                issues = ["Policy violations detected. Please review the dashboard manually for details."]
                
            return {
                "has_issues": has_issues,
                "issues": issues,
                "raw_text_preview": page_text[:500].replace('\n', ' ')
            }
            
        finally:
            await page.close()
