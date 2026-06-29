import asyncio
import json
from admob_core.client import AdMobClient
from admob_core.config import Config
import admob_mcp.server as server

async def dump_mapping():
    config = Config()
    server.client = AdMobClient(config.publisher_id)
    try:
        mappings = await server.client.list_ad_unit_mappings("7822211935")
        if mappings:
            print("Existing mappings:")
            print(json.dumps(mappings[0], indent=2))
        else:
            print("No mappings found.")
    finally:
        await server.client.close()

if __name__ == "__main__":
    asyncio.run(dump_mapping())
