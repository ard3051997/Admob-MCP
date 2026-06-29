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

@mcp.prompt()
def setup_mediation(app_id: str, ad_format: str, target_geos: str):
    """Guided prompt for creating a new mediation group with floors and bidding."""
    return f"""
    Please help me set up a new mediation group for app_id {app_id}.
    Format: {ad_format}
    Target Geos (comma separated): {target_geos}
    
    Follow these steps:
    1. Check `admob_list_ad_units` to find the correct ad unit ID for {app_id} and {ad_format}.
    2. Use `admob_recommend_networks_geo` for the target geos to see which networks are Tier 1.
    3. If we don't have ad unit mappings for the chosen networks, ask the user for the network credentials and use `admob_create_ad_unit_mapping` to link them.
    4. Build the group using `admob_build_mediation_group` with `dry_run=True`. Include bidding lines and waterfall lines with appropriate floors based on historical data.
    5. Show me the dry run result and ask for my confirmation before running without dry_run.
    """
