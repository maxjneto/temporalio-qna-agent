"""Temporal Activities - Search execution via MCP."""

import json
from typing import Any, Dict, List

from temporalio import activity

@activity.defn
async def mcp_search_activity(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """Activity that connects to MCP Server and executes semantic search.
    
    Args:
        query: Search text
        top_k: Number of results to return
        
    Returns:
        List of found documents with id, score and chunk
    """
    from fastmcp import Client

    MCP_CMD = "mcp_server.py"
    
    async with Client(MCP_CMD) as client:
        resp = await client.call_tool(
            "azure_ai_search", {"query": query, "top_k": top_k}
        )
        return json.loads(resp.content[0].text)