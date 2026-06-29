from typing import Dict, Any, List, Optional
from admob_mcp.server import mcp
import admob_mcp.server as server
from admob_core.registry import AdSourceRegistry
from admob_core.builder import MediationGroupBuilder

@mcp.tool()
async def admob_list_mediation_groups():
    """List all mediation groups with their targeting and lines."""
    try:
        return await server.client.list_mediation_groups()
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

@mcp.tool()
async def admob_list_ad_sources():
    """List all available ad sources."""
    try:
        return await server.client.list_ad_sources()
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

@mcp.tool()
async def admob_create_mediation_group(group: Dict[str, Any], dry_run: bool = False):
    """
    Create a new mediation group (raw payload). 
    Consider using admob_build_mediation_group for a guided experience.
    Safety: Runs rules engine validation before execution.
    """
    try:
        validation_results = server.rules_engine.validate_mediation_group(group)
        
        if any(r.severity.value == "BLOCK" for r in validation_results):
            return {
                "status": "ERROR",
                "message": "Validation failed with blocking issues.",
                "validation_results": [r.to_dict() for r in validation_results]
            }

        if dry_run:
            return server.safety_layer.dry_run_response("CREATE_MEDIATION_GROUP", group, [r.to_dict() for r in validation_results])

        result = await server.client.create_mediation_group(group)
        server.safety_layer.log_operation({
            "tool": "admob_create_mediation_group",
            "publisher_id": server.client.publisher_id,
            "request": group,
            "response": result,
            "validation_results": [r.to_dict() for r in validation_results]
        })
        return result
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

@mcp.tool()
async def admob_update_mediation_group(group_id: str, group: Dict[str, Any], update_mask: str, dry_run: bool = False):
    """
    Update an existing mediation group with a raw payload and update_mask.
    Safety: Captures snapshot before update.
    """
    try:
        if dry_run:
            return server.safety_layer.dry_run_response("UPDATE_MEDIATION_GROUP", group, [])

        all_groups = await server.client.list_mediation_groups()
        snapshot = next((g for g in all_groups if g.get("mediationGroupId") == group_id or g.get("name", "").endswith(group_id)), None)
        
        # Get true group id
        actual_group_id = snapshot.get("name").split("/")[-1] if snapshot else group_id
        
        result = await server.client.update_mediation_group(actual_group_id, group, update_mask)
        
        server.safety_layer.log_operation({
            "tool": "admob_update_mediation_group",
            "publisher_id": server.client.publisher_id,
            "resource_id": actual_group_id,
            "snapshot_before": snapshot,
            "request": group,
            "response": result
        })
        return result
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

@mcp.tool()
async def admob_create_ad_unit_mapping(ad_unit_id: str, ad_source_id: str, adapter_id: str, mapping_params: Dict[str, str], display_name: str = ""):
    """Create a new ad unit mapping (link third-party network credentials to an ad unit)."""
    try:
        # Validate params
        required = AdSourceRegistry.get_mapping_params(ad_source_id)
        missing = [p for p in required if p not in mapping_params]
        if missing:
            return {"status": "ERROR", "message": f"Missing required mapping params for {ad_source_id}: {missing}"}
            
        unit_id = ad_unit_id.split("/")[-1]
            
        mapping = {
            "adSourceId": ad_source_id,
            "adapterId": adapter_id,
            "adUnitMappingParams": mapping_params,
            "state": "ENABLED"
        }
        if display_name:
            mapping["displayName"] = display_name
            
        return await server.client.create_ad_unit_mapping(unit_id, mapping)
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

@mcp.tool()
async def admob_list_ad_unit_mappings(ad_unit_id: str):
    """List existing ad unit mappings for a specific ad unit."""
    try:
        unit_id = ad_unit_id.split("/")[-1]
        return await server.client.list_ad_unit_mappings(unit_id)
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

@mcp.tool()
async def admob_set_floor(group_id: str, line_id: str, floor_cpm: float, dry_run: bool = False):
    """Set or update the eCPM floor price (in dollars) for a specific waterfall mediation line item."""
    try:
        if dry_run:
            return server.safety_layer.dry_run_response("SET_FLOOR", {"group_id": group_id, "line_id": line_id, "floor_cpm": floor_cpm}, [])

        all_groups = await server.client.list_mediation_groups()
        snapshot = next((g for g in all_groups if g.get("mediationGroupId") == group_id or g.get("name", "").endswith(group_id)), None)
        if not snapshot:
             return {"status": "ERROR", "message": f"Group {group_id} not found."}
             
        actual_group_id = snapshot.get("name").split("/")[-1]

        cpm_micros = str(int(round(floor_cpm * 1_000_000)))
        
        update_mask = f'mediationGroupLines["{line_id}"].cpmMicros,mediationGroupLines["{line_id}"].cpmMode'
        patch_payload = {
            "mediationGroupLines": {
                 line_id: {
                      "cpmMode": "MANUAL",
                      "cpmMicros": cpm_micros
                 }
            }
        }
        
        result = await server.client.update_mediation_group(actual_group_id, patch_payload, update_mask)
        
        server.safety_layer.log_operation({
            "tool": "admob_set_floor",
            "publisher_id": server.client.publisher_id,
            "resource_id": actual_group_id,
            "snapshot_before": snapshot,
            "request": patch_payload,
            "response": result
        })
        return result
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

@mcp.tool()
async def admob_add_mediation_line(group_id: str, ad_source_id: str, cpm_mode: str, 
                                   floor_cpm: float = 0.0, ad_unit_mapping_id: str = "",
                                   dry_run: bool = False):
    """Add a new line (bidding or waterfall) to an existing mediation group."""
    try:
        all_groups = await server.client.list_mediation_groups()
        snapshot = next((g for g in all_groups if g.get("mediationGroupId") == group_id or g.get("name", "").endswith(group_id)), None)
        if not snapshot:
             return {"status": "ERROR", "message": f"Group {group_id} not found."}
             
        actual_group_id = snapshot.get("name").split("/")[-1]

        line_id = "-1"
        line = {
            "adSourceId": ad_source_id,
            "cpmMode": cpm_mode.upper(),
            "state": "ENABLED"
        }
        if cpm_mode.upper() == "MANUAL":
            line["cpmMicros"] = str(int(round(floor_cpm * 1_000_000)))
            
        if ad_unit_mapping_id:
             line["adUnitMappingId"] = ad_unit_mapping_id

        # Validate with rules engine
        test_group = dict(snapshot)
        lines = dict(test_group.get("mediationGroupLines", {}))
        lines[line_id] = line
        test_group["mediationGroupLines"] = lines
        
        validation_results = server.rules_engine.validate_mediation_group(test_group)
        if any(r.severity.value == "BLOCK" for r in validation_results):
            return {
                "status": "ERROR",
                "message": "Validation failed with blocking issues.",
                "validation_results": [r.to_dict() for r in validation_results]
            }

        if dry_run:
            return server.safety_layer.dry_run_response("ADD_MEDIATION_LINE", line, [r.to_dict() for r in validation_results])
            
        update_mask = f'mediationGroupLines["{line_id}"]'
        patch_payload = {
            "mediationGroupLines": {
                 line_id: line
            }
        }
        
        result = await server.client.update_mediation_group(actual_group_id, patch_payload, update_mask)
        
        server.safety_layer.log_operation({
            "tool": "admob_add_mediation_line",
            "publisher_id": server.client.publisher_id,
            "resource_id": actual_group_id,
            "snapshot_before": snapshot,
            "request": patch_payload,
            "response": result
        })
        return result
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

@mcp.tool()
async def admob_build_mediation_group(display_name: str, platform: str, ad_format: str,
                                      bidding_sources: List[Dict[str, str]], 
                                      waterfall_sources: List[Dict[str, Any]],
                                      included_countries: List[str] = [],
                                      excluded_countries: List[str] = [],
                                      dry_run: bool = False):
    """
    Guided mediation group creation using MediationGroupBuilder.
    bidding_sources format: [{"ad_source_id": "...", "ad_unit_mapping_id": "..."}, ...]
    waterfall_sources format: [{"ad_source_id": "...", "floor_cpm": 1.5, "ad_unit_mapping_id": "..."}, ...]
    """
    try:
        builder = MediationGroupBuilder(display_name, platform, ad_format, included_countries, excluded_countries)
        
        for bs in bidding_sources:
             builder.add_bidding_line(bs["ad_source_id"], bs.get("ad_unit_mapping_id"))
             
        for ws in waterfall_sources:
             builder.add_waterfall_line(ws["ad_source_id"], float(ws.get("floor_cpm", 0.01)), ws.get("ad_unit_mapping_id"))
             
        group_payload = builder.build()
        
        validation_results = server.rules_engine.validate_mediation_group(group_payload)
        
        if any(r.severity.value == "BLOCK" for r in validation_results):
            return {
                "status": "ERROR",
                "message": "Validation failed with blocking issues.",
                "validation_results": [r.to_dict() for r in validation_results]
            }

        if dry_run:
            return server.safety_layer.dry_run_response("BUILD_MEDIATION_GROUP", group_payload, [r.to_dict() for r in validation_results])

        result = await server.client.create_mediation_group(group_payload)
        server.safety_layer.log_operation({
            "tool": "admob_build_mediation_group",
            "publisher_id": server.client.publisher_id,
            "request": group_payload,
            "response": result,
            "validation_results": [r.to_dict() for r in validation_results]
        })
        return result
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}
