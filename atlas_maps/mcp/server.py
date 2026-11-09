"""Model Context Protocol (MCP) server for Maps & Geospatial Intelligence."""
from __future__ import annotations

import json
from typing import Optional
from fastmcp import FastMCP
from atlas_maps.core.wire import SpatialViewport, build_search_url
from atlas_maps.core.parsers import extract_initialization_state, parse_place_entries
from atlas_maps.transport.client import MapsClient

mcp = FastMCP("AtlasMaps")


@mcp.tool()
def search_places(query: str, lat: Optional[float] = None, lng: Optional[float] = None) -> str:
    """
    Search places, businesses, and coordinates using direct wire Google Maps retrieval.
    Args:
        query: Search term (e.g., 'Specialty Coffee London', 'Data Centers Frankfurt')
        lat: Optional center latitude for spatial bounding
        lng: Optional center longitude for spatial bounding
    """
    viewport = None
    if lat is not None and lng is not None:
        viewport = SpatialViewport(center_lat=lat, center_lng=lng)
        
    url = build_search_url(query, viewport)
    client = MapsClient()
    
    try:
        html = client.fetch_page(url)
        state = extract_initialization_state(html)
        if not state:
            return json.dumps({"status": "no_records", "query": query, "items": []})
            
        places = parse_place_entries(state)
        return json.dumps({
            "status": "success",
            "count": len(places),
            "results": [p.model_dump() for p in places]
        }, indent=2)
    except Exception as exc:
        return json.dumps({"status": "error", "message": str(exc)})


if __name__ == "__main__":
    mcp.run()
