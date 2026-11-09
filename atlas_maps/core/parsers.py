"""Stream and regex parsers for Google Maps initial state payloads."""
from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Optional
from atlas_maps.models.place import GeoCoordinates, PlaceMetadata

logger = logging.getLogger("atlas_maps.parsers")

# Google Maps state blob pattern
STATE_PATTERN = re.compile(r"window\.APP_INITIALIZATION_STATE\s*=\s*(\[.*?\])\s*;", re.DOTALL)
# Search RPC embedded array pattern
RPC_PATTERN = re.compile(r"/\*.*?blob.*?\*/\s*(\[.*\])", re.DOTALL)


def extract_initialization_state(html: str) -> Optional[List[Any]]:
    """Extract APP_INITIALIZATION_STATE JSON structure from Google Maps HTML."""
    match = STATE_PATTERN.search(html)
    if not match:
        return None
    raw_str = match.group(1)
    try:
        return json.loads(raw_str)
    except json.JSONDecodeError as exc:
        logger.warning(f"Malformed initialization state JSON: {exc}")
        return None


def parse_place_entries(state: List[Any]) -> List[PlaceMetadata]:
    """
    Parse places records from nested dense positional arrays.
    Engineered to handle schema shifts gracefully without throwing unhandled exceptions.
    """
    places: List[PlaceMetadata] = []
    
    try:
        if not (isinstance(state, list) and len(state) > 3 and isinstance(state[3], list)):
            return places
            
        data_block = state[3]
        target_rows: List[Any] = []
        
        # Recursively find rows that resemble place listings
        def find_rows(node: Any) -> None:
            if not isinstance(node, list):
                return
            # If this list has row elements where row[11] is a string and row[10] exists
            if len(node) > 13 and isinstance(node[11], str) and (isinstance(node[10], (str, int)) or node[10] is not None):
                target_rows.append(node)
                return
            for sub in node:
                find_rows(sub)

        find_rows(data_block)
                
        for row in target_rows:
            try:
                title = row[11] if len(row) > 11 and isinstance(row[11], str) else None
                if not title:
                    continue
                    
                place_id = str(row[10]) if len(row) > 10 and row[10] is not None else f"pid_{hash(title)}"
                
                # Rating and review count
                rating = None
                reviews = None
                if len(row) > 4 and isinstance(row[4], list) and len(row[4]) > 7:
                    rating = float(row[4][7]) if row[4][7] is not None else None
                    reviews = int(row[4][8]) if len(row[4]) > 8 and row[4][8] is not None else None
                
                # Category
                category = row[13][0] if len(row) > 13 and isinstance(row[13], list) and len(row[13]) > 0 else None
                
                # Coordinates
                coords = None
                if len(row) > 9 and isinstance(row[9], list) and len(row[9]) >= 4:
                    lat, lng = row[9][2], row[9][3]
                    if isinstance(lat, (int, float)) and isinstance(lng, (int, float)):
                        coords = GeoCoordinates(latitude=float(lat), longitude=float(lng))

                places.append(PlaceMetadata(
                    place_id=place_id,
                    title=title,
                    category=category,
                    rating=rating,
                    review_count=reviews,
                    coordinates=coords
                ))
            except Exception as item_err:
                logger.debug(f"Row skip due to variation: {item_err}")
                continue

    except Exception as e:
        logger.error(f"Top-level parse error: {e}", exc_info=True)

    return places
