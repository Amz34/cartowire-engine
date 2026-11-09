"""Tests for grid decomposition, concurrency, and EGM orchestration."""
import asyncio
import pytest
from atlas_maps.core.grid import BoundingBox, METROPOLITAN_PRESETS
from atlas_maps.core.concurrency import TokenBucketRateLimiter
from atlas_maps.core.orchestrator import ElephantCoordinator, SwarmMetrics
from atlas_maps.models.place import PlaceMetadata


def test_bounding_box_partitioning():
    bbox = BoundingBox(min_lat=40.0, min_lng=-74.0, max_lat=41.0, max_lng=-73.0)
    cells = bbox.partition(rows=2, cols=2)
    assert len(cells) == 4
    
    # Check bounds
    assert cells[0].center_lat < cells[2].center_lat
    assert cells[0].center_lng < cells[1].center_lng


def test_token_bucket_rate_limiter():
    async def run():
        limiter = TokenBucketRateLimiter(rate=10.0, capacity=2.0)
        await limiter.acquire()
        await limiter.acquire()
    asyncio.run(run())


def test_metropolitan_presets_validity():
    for name, bbox in METROPOLITAN_PRESETS.items():
        assert bbox.max_lat > bbox.min_lat
        assert bbox.max_lng > bbox.min_lng
        cells = bbox.partition(rows=2, cols=2)
        assert len(cells) == 4
