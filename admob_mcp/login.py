import asyncio
import os
from playwright.async_api import async_playwright

SESSION_DIR = ".admob_session"

async def main():
    print("=== AdMob Headful Login ===")
    print("This will open a visible browser window.")
    print("Please log in to your Google Account associated with AdMob.")
    print("Once you reach the AdMob dashboard, the session will be saved automatically.")
    print("Close the browser window when you are done.\n")
    
    os.makedirs(SESSION_DIR, exist_ok=True)
    
    async with async_playwright() as p:
        # Launch headed browser
        browser = await p.chromium.launch(headless=False)
        
        # Create a persistent context to save cookies and local storage
        context = await p.chromium.launch_persistent_context(
            user_data_dir=SESSION_DIR,
            headless=False,
            viewport={"width": 1280, "height": 800},
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        page = await context.new_page()
        
        # Navigate to AdMob
        await page.goto("https://apps.admob.com/")
        
        print("Browser opened! Please log in to AdMob.")
        print("Waiting for you to close the browser window...")
        
        # Wait until the user closes the browser context
        try:
            while len(context.pages) > 0:
                await asyncio.sleep(1)
        except Exception:
            pass
            
        print("\nSession saved to .admob_session/")
        print("You can now use the browser automation tools!")

if __name__ == "__main__":
    asyncio.run(main())
