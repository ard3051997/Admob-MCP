import asyncio
from contextlib import asynccontextmanager
from fastmcp import FastMCP
from admob_core.config import Config

# Initialize config early (this is safe — just reads yaml/env)
config = Config()

# Core components — initialized lazily in lifespan
client = None
db = None
expert = None
rules_engine = None
safety_layer = None

@asynccontextmanager
async def lifespan(app):
    global client, db, expert, rules_engine, safety_layer
    from admob_core.client import AdMobClient
    from admob_core.db import AdMobDB
    from admob_core.analyzer import AdMonExpert
    from admob_core.rules import RulesEngine
    from admob_core.safety import SafetyLayer

    client = AdMobClient()
    db = AdMobDB()
    expert = AdMonExpert(client, db)
    rules_engine = RulesEngine(config)
    safety_layer = SafetyLayer(config.audit_log_path)
    try:
        yield
    finally:
        await client.close()

# Initialize MCP server
mcp = FastMCP("AdMob Mediation", lifespan=lifespan)

# Import tools to register them
import admob_mcp.tools.reporting
import admob_mcp.tools.management
import admob_mcp.tools.experiments
import admob_mcp.tools.diagnostics
import admob_mcp.tools.browser
import admob_mcp.resources
import admob_mcp.prompts

if __name__ == "__main__":
    mcp.run()

