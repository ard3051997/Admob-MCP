from admob_mcp.server import mcp
import admob_mcp.server as server
from admob_core.registry import AdSourceRegistry
from typing import Optional

@mcp.tool()
async def admob_expert_sync(app_name: str):
    """
    Sync historical data for an app into the local expert database.
    Use this before running analysis on a new app.
    """
    try:
        app_id = await server.expert.sync_app_data(app_name)
        return f"Successfully synced data for '{app_name}' ({app_id}). Expert is ready for analysis."
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

@mcp.tool()
async def admob_expert_analyze(app_name: str):
    """
    Run the 'Ad Monetization Expert' analysis on an app.
    Performs baseline check and anomaly investigation (per play.md).
    """
    try:
        app_id = server.expert.db.get_app_id_by_name(app_name)
        if not app_id:
            return f"App '{app_name}' not found in local DB. Please run 'admob_expert_sync' first."
        
        analysis_report = await server.expert.analyze_app(app_id)
        return analysis_report
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

@mcp.tool()
async def admob_recommend_networks_geo(country_code: str, ad_format: str):
    """
    Get geo-aware network recommendations for a specific country and format.
    Powered by the Geo-Inventory Strength matrix.
    """
    try:
        recommendations = AdSourceRegistry.recommend_networks_for_geo(country_code, ad_format)
        
        report = f"# Geo-Aware Recommendations for {country_code} ({ad_format})\n"
        for tier in ["T1", "T2"]:
            report += f"## {tier} (Strong Demand)\n"
            for rec in recommendations[tier]:
                report += f"- **{rec['name']}**: {rec['notes']}\n"
                
        return report
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

@mcp.tool()
async def admob_request_placement_map():
    """
    Returns a template for the user to provide a Placement Map.
    Essential for UX-aware optimization.
    """
    template = """
# Placement Map Template
Please fill this out to help me optimize your UX/Revenue balance:

| Screen Name | Ad Format | Ad Unit ID | Purpose | Frequency / Trigger |
|-------------|-----------|------------|---------|---------------------|
| Home Screen | Banner    | ...        | Anchor  | Persistent          |
| Level End   | Interstitial| ...      | Break   | Every 2 levels      |
| Shop        | Rewarded  | ...        | Unlock  | User opt-in         |
    """
    return template

