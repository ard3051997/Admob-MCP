from admob_mcp.server import mcp
from admob_core.browser_control import BrowserControl
import admob_mcp.server as server

# Singleton browser control
_browser = None

def get_browser():
    global _browser
    if _browser is None:
        _browser = BrowserControl()
    return _browser

@mcp.tool()
async def admob_policy_violations():
    """Check the AdMob Policy Center for account or app-level violations using browser automation. Note: Requires the user to run python -m admob_mcp.login first."""
    try:
        browser = get_browser()
        result = await browser.fetch_policy_issues()
        
        status_text = "ISSUES DETECTED!" if result["has_issues"] else "No policy issues found."
        output = f"Policy Center Status: {status_text}\n\n"
        
        if result["issues"]:
            for i, issue in enumerate(result["issues"], 1):
                output += f"{i}. {issue}\n"
                
        return output
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

@mcp.tool()
async def admob_realtime_metrics():
    """Check today's live metrics from the AdMob Dashboard using browser automation."""
    return {"status": "NOT_IMPLEMENTED", "message": "Realtime metrics scraping is planned for next iteration."}
