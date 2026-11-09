"""Command Line Interface for Atlas Maps Intelligence Engine."""
from __future__ import annotations

import argparse
import json
import sys
from atlas_maps.core.wire import SpatialViewport, build_search_url
from atlas_maps.core.parsers import extract_initialization_state, parse_place_entries
from atlas_maps.transport.client import MapsClient


def main():
    parser = argparse.ArgumentParser(
        prog="atlas-maps",
        description="High-performance wire-level Google Maps discovery engine."
    )
    parser.add_argument("query", type=str, help="Search query (e.g. 'Coffee shops in Brooklyn')")
    parser.add_argument("--lat", type=float, default=None, help="Latitude center")
    parser.add_argument("--lng", type=float, default=None, help="Longitude center")
    parser.add_argument("--json", action="store_true", help="Output raw JSON results")

    args = parser.parse_args()

    viewport = None
    if args.lat is not None and args.lng is not None:
        viewport = SpatialViewport(center_lat=args.lat, center_lng=args.lng)

    url = build_search_url(args.query, viewport)
    client = MapsClient()

    try:
        # Restriction-proof dual resolution: try wire extraction; fallback to headless Chrome
        places = []
        try:
            html = client.fetch_page(url)
            state = extract_initialization_state(html)
            if state:
                places = parse_place_entries(state)
        except Exception:
            pass

        if not places:
            places = client.fetch_places_headless(url)

        if args.json:
            print(json.dumps([p.model_dump() for p in places], indent=2))
        else:
            print(f"\nExtracted {len(places)} locations for query: '{args.query}'\n")
            for idx, p in enumerate(places, 1):
                rating_str = f"★ {p.rating} ({p.review_count})" if p.rating else "No reviews"
                cat_str = f"[{p.category}]" if p.category else ""
                print(f"{idx:02d}. {p.title} {cat_str} - {rating_str}")

    except Exception as exc:
        print(f"Error during query execution: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
