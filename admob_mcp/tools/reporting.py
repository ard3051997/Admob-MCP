from typing import List, Optional
from admob_mcp.server import mcp
import admob_mcp.server as server
from admob_core.models.reports import ReportSpec, DateRange

@mcp.tool()
async def admob_list_apps():
    """List all apps in the AdMob account."""
    try:
        apps = await server.client.list_apps()
        return [app.model_dump() for app in apps]
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

@mcp.tool()
async def admob_list_ad_units(app_id: Optional[str] = None):
    """List all ad units, optionally filtered by app_id."""
    try:
        units = await server.client.list_ad_units(app_id)
        return [unit.model_dump() for unit in units]
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

@mcp.tool()
async def admob_network_report(start_date: str, end_date: str, dimensions: Optional[List[str]] = None, metrics: Optional[List[str]] = None):
    """Generate an AdMob Network report."""
    try:
        if dimensions is None:
            dimensions = ["DATE", "APP", "AD_UNIT", "COUNTRY"]
        if metrics is None:
            metrics = ["ESTIMATED_EARNINGS", "IMPRESSIONS", "IMPRESSION_RPM", "MATCH_RATE"]
        
        spec = ReportSpec(
            date_range=DateRange(start_date=start_date, end_date=end_date),
            dimensions=dimensions,
            metrics=metrics
        )
        report = await server.client.generate_network_report(spec)
        return [row.model_dump() for row in report.rows]
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

@mcp.tool()
async def admob_mediation_report(start_date: str, end_date: str, dimensions: Optional[List[str]] = None, metrics: Optional[List[str]] = None):
    """Generate an AdMob Mediation report."""
    try:
        if dimensions is None:
            dimensions = ["DATE", "APP", "AD_UNIT", "AD_SOURCE", "COUNTRY"]
        if metrics is None:
            metrics = ["ESTIMATED_EARNINGS", "IMPRESSIONS", "IMPRESSION_RPM", "MATCH_RATE"]
        
        spec = ReportSpec(
            date_range=DateRange(start_date=start_date, end_date=end_date),
            dimensions=dimensions,
            metrics=metrics
        )
        report = await server.client.generate_mediation_report(spec)
        return [row.model_dump() for row in report.rows]
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

