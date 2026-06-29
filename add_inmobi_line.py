import asyncio
from admob_core.client import AdMobClient
from admob_core.config import Config
import admob_mcp.server as server

async def add_inmobi():
    config = Config()
    server.client = AdMobClient(config.publisher_id)
    
    group_id = "4127212122" # India GST Calculator: GSTCalcy_Banner_WW
    
    # InMobi (SDK) (bidding) Source ID
    ad_source_id = "8468954295581492586"
    # InMobi (SDK) - Bidding Banner Android SDK Adapter ID
    adapter_id = "540"
    
    # Ad units targeted by this group
    ad_unit_ids = [
        "7822211935",
        "3310681893"
    ]
    
    # Configuration metadata for this adapter
    # 621 = Account ID, 622 = Placement ID
    ad_unit_configs = {
        "621": "f7cbf1c66bfb4aeaa0779a1cab242d7c",
        "622": "10000738964"
    }
    
    try:
        ad_unit_mappings_dict = {}
        
        # 1. Create mapping for each ad unit
        print("Creating Ad Unit Mappings for InMobi SDK (Bidding)...")
        for unit_id in ad_unit_ids:
            # Check if mapping already exists
            existing_mappings = await server.client.list_ad_unit_mappings(unit_id)
            existing = next((m for m in existing_mappings if m.get("adapterId") == adapter_id), None)
            
            if existing:
                print(f"Mapping already exists for {unit_id}: {existing['name']}")
                mapping_name = existing["name"]
            else:
                mapping = {
                    "adapterId": adapter_id,
                    "adUnitConfigurations": ad_unit_configs,
                    "state": "ENABLED",
                    "displayName": "InMobi SDK Bidding"
                }
                # The API requires wrapping it inside an object when hitting adUnits endpoint? No, just sending it.
                res = await server.client.create_ad_unit_mapping(unit_id, mapping)
                mapping_name = res["name"]
                print(f"Created mapping for {unit_id}: {mapping_name}")
                
            full_unit_id = f"ca-app-pub-9800009975517669/{unit_id}"
            ad_unit_mappings_dict[full_unit_id] = mapping_name

        # 2. Add mediation line to group
        print("\nAdding InMobi SDK Bidding line to group...")
        all_groups = await server.client.list_mediation_groups()
        snapshot = next((g for g in all_groups if g.get("mediationGroupId") == group_id), None)
        
        line_id = "-1"
        line = {
            "displayName": "InMobi Bidding",
            "adSourceId": ad_source_id,
            "cpmMode": "LIVE",
            "state": "ENABLED",
            "adUnitMappings": ad_unit_mappings_dict
        }
        
        # Using the whole mediationGroupLines["-1"] object as the field mask
        # Since it's a new line, it won't overwrite existing ones
        update_mask = f'mediationGroupLines["{line_id}"]'
        patch_payload = {
            "mediationGroupLines": {
                 line_id: line
            }
        }
        
        result = await server.client.update_mediation_group(group_id, patch_payload, update_mask)
        print("\nSuccess! Added InMobi SDK Bidding line.")
        
        # Print resulting lines to confirm
        print("\nCurrent lines in group:")
        for lid, l in result.get("mediationGroupLines", {}).items():
            print(f" - {l.get('displayName', 'Unknown')} (Mode: {l.get('cpmMode')}) - Source: {l.get('adSourceId')}")
            
    except Exception as e:
        print(f"Failed: {e}")
    finally:
        await server.client.close()

if __name__ == "__main__":
    asyncio.run(add_inmobi())
