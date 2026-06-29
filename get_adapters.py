import asyncio
import json
from admob_core.client import AdMobClient
from admob_core.config import Config
import admob_mcp.server as server

async def get_all_sources():
    config = Config()
    client = AdMobClient(config.publisher_id)
    
    try:
        data = await client._request("GET", f"accounts/{config.publisher_id}/adSources")
        sources = data.get("adSources", [])
        for s in sources:
            if "InMobi" in s.get("title", ""):
                print(json.dumps(s, indent=2))
                
                # Fetch adapters for this source
                name = s.get("name") # e.g., accounts/.../adSources/...
                if name:
                    adapters = await client._request("GET", f"{name}/adapters")
                    print(f"Adapters for {name}:")
                    print(json.dumps(adapters, indent=2))
    except Exception as e:
        print(f"Failed: {e}")
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(get_all_sources())
