from admob_mcp.server import mcp
import admob_mcp.server as server

@mcp.tool()
async def admob_create_ab_experiment(group_id: str, experiment: dict, dry_run: bool = False):
    """Create a mediation A/B experiment."""
    try:
        if dry_run:
            return server.safety_layer.dry_run_response("CREATE_AB_EXPERIMENT", experiment, [])
        
        result = await server.client.create_ab_experiment(group_id, experiment)
        server.safety_layer.log_operation({
            "tool": "admob_create_ab_experiment",
            "group_id": group_id,
            "request": experiment,
            "response": result
        })
        return result
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

@mcp.tool()
async def admob_stop_ab_experiment(group_id: str, experiment_id: str, winner: str):
    """Stop an A/B experiment and pick the winner."""
    try:
        result = await server.client.stop_ab_experiment(group_id, experiment_id, winner)
        server.safety_layer.log_operation({
            "tool": "admob_stop_ab_experiment",
            "group_id": group_id,
            "experiment_id": experiment_id,
            "winner": winner,
            "response": result
        })
        return result
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

