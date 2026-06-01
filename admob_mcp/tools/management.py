from typing import Dict, Any, List
from admob_mcp.server import mcp
import admob_mcp.server as server

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
    Create a new mediation group.
    Safety: Runs rules engine validation before execution.
    """
    try:
        validation_results = server.rules_engine.validate_mediation_group(group)
        
        # Check for BLOCK severity
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
    Update an existing mediation group.
    Safety: Captures snapshot before update.
    """
    try:
        if dry_run:
            return server.safety_layer.dry_run_response("UPDATE_MEDIATION_GROUP", group, [])

        # Snapshot before: fetch all groups and find the target
        all_groups = await server.client.list_mediation_groups()
        snapshot = next((g for g in all_groups if g.get("mediationGroupId") == group_id or g.get("name", "").endswith(group_id)), None)
        
        result = await server.client.update_mediation_group(group_id, group, update_mask)
        
        server.safety_layer.log_operation({
            "tool": "admob_update_mediation_group",
            "publisher_id": server.client.publisher_id,
            "resource_id": group_id,
            "snapshot_before": snapshot,
            "request": group,
            "response": result
        })
        return result
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

