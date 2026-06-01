from admob_mcp.server import mcp

@mcp.prompt()
def optimize_app(app_id: str):
    """Prompt template for optimizing an app's monetization."""
    return f"""
    Please perform a full optimization check for app ID: {app_id}.
    1. Run `admob_expert_analyze` to find existing issues.
    2. Check the current mediation groups and ad sources.
    3. Generate a mediation report for the last 7 days to check eCPM performance.
    4. Suggest optimizations based on `admob_recommend_networks_geo` and observed performance.
    """

@mcp.prompt()
def portfolio_health():
    """Prompt template for a global portfolio health check."""
    return """
    Check the health of the entire AdMob portfolio.
    1. List all apps.
    2. For each major app (by revenue), run diagnostics.
    3. Look for stale A/B experiments across all groups.
    4. Summarize revenue performance for the last 30 days.
    """
