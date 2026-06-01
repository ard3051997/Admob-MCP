import json
from admob_mcp.server import mcp, config
from admob_core.registry import AdSourceRegistry

@mcp.resource("admob://ad-sources")
def get_ad_sources_resource():
    """Returns the full ad source registry with bidding support and IDs."""
    return json.dumps(AdSourceRegistry.SOURCES, indent=2)

@mcp.resource("admob://app-categories")
def get_app_categories_resource():
    """Returns the app category definitions from config."""
    return json.dumps(config.app_categories, indent=2)

@mcp.resource("admob://format-support")
def get_format_support_resource():
    """Returns the format support matrix per ad source."""
    return json.dumps(AdSourceRegistry.FORMAT_SUPPORT, indent=2)
