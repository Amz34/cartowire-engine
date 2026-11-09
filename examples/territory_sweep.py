"""Demonstration of large-scale metropolitan territorial sweeps using the EGM pattern."""
import asyncio
import json
from atlas_maps.core.grid import METROPOLITAN_PRESETS
from atlas_maps.core.orchestrator import ElephantCoordinator


async def run_manhattan_sweep():
    coordinator = ElephantCoordinator(rate_limit_rps=3.0)
    bbox = METROPOLITAN_PRESETS["manhattan"]
    
    print("Initiating territorial grid sweep across Central Manhattan...")
    places, metrics = await coordinator.run_territory_sweep(
        query="Independent Specialty Coffee",
        bounding_box=bbox,
        grid_rows=2,
        grid_cols=2,
        concurrency=2,
    )
    
    print("\n--- Swarm Execution Metrics ---")
    print(f"Total Grid Cells Evaluated: {metrics.total_grid_cells}")
    print(f"Raw Entities Detected:       {metrics.raw_places_extracted}")
    print(f"Unique Commercial Venues:    {metrics.unique_places_retained}")
    print(f"Deduplication Ratio:         {metrics.deduplication_ratio * 100:.1f}%\n")
    
    for idx, place in enumerate(places[:10], 1):
        print(f"{idx:02d}. {place.title} | Rating: {place.rating} ({place.review_count} reviews)")


if __name__ == "__main__":
    asyncio.run(run_manhattan_sweep())
