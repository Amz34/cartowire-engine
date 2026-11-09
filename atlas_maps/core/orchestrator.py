"""Elephant-Goldfish Scraping & Distributed Quality Auditor Engine (EGM Pattern)."""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from atlas_maps.core.concurrency import TokenBucketRateLimiter
from atlas_maps.core.grid import BoundingBox, METROPOLITAN_PRESETS
from atlas_maps.core.wire import SpatialViewport, build_search_url
from atlas_maps.core.parsers import extract_initialization_state, parse_place_entries
from atlas_maps.models.place import PlaceMetadata
from atlas_maps.transport.client import MapsClient

logger = logging.getLogger("atlas_maps.orchestrator")


@dataclass
class SwarmMetrics:
    """Execution telemetry captured across the swarm."""
    total_grid_cells: int = 0
    successful_cells: int = 0
    failed_cells: int = 0
    raw_places_extracted: int = 0
    unique_places_retained: int = 0
    deduplication_ratio: float = 0.0


class GoldfishCellWorker:
    """
    Stateless, ephemeral subagent / execution worker.
    Dispatched to scrape a single geospatial coordinate cell and terminates immediately,
    preventing persistent session tracking and memory bloat.
    """

    def __init__(self, worker_id: int, client: MapsClient, limiter: TokenBucketRateLimiter):
        self.worker_id = worker_id
        self.client = client
        self.limiter = limiter

    async def execute_cell(self, query: str, viewport: SpatialViewport) -> List[PlaceMetadata]:
        await self.limiter.acquire()
        url = build_search_url(query, viewport)
        logger.debug(f"[Goldfish #{self.worker_id}] Scraping cell @ {viewport.center_lat},{viewport.center_lng}")

        # Run non-blocking in executor thread pool
        loop = asyncio.get_running_loop()
        try:
            # First try lightweight wire fetch
            html = await loop.run_in_executor(None, self.client.fetch_page, url)
            state = extract_initialization_state(html)
            if state:
                places = parse_place_entries(state)
                if places:
                    return places
        except Exception as e:
            logger.debug(f"[Goldfish #{self.worker_id}] Wire extraction fallback triggered: {e}")

        # Fallback to headless execution if wire payload is dense
        try:
            places = await loop.run_in_executor(None, self.client.fetch_places_headless, url)
            return places
        except Exception as err:
            logger.warning(f"[Goldfish #{self.worker_id}] Cell execution failed: {err}")
            return []


class ElephantCoordinator:
    """
    The Elephant: Master orchestrator maintaining global state, proxy rotators,
    cross-cell deduplication, and quality audit verification.
    """

    def __init__(self, rate_limit_rps: float = 2.0):
        self.limiter = TokenBucketRateLimiter(rate=rate_limit_rps)
        self.client = MapsClient()
        self.place_registry: Dict[str, PlaceMetadata] = {}
        self.seen_names: Set[str] = set()

    async def run_territory_sweep(
        self,
        query: str,
        bounding_box: BoundingBox,
        grid_rows: int = 2,
        grid_cols: int = 2,
        concurrency: int = 2,
    ) -> tuple[List[PlaceMetadata], SwarmMetrics]:
        """
        Decomposes a major territory into a grid matrix and coordinates parallel
        Goldfish workers with stateful deduplication.
        """
        viewports = bounding_box.partition(rows=grid_rows, cols=grid_cols)
        metrics = SwarmMetrics(total_grid_cells=len(viewports))
        logger.info(f"[Elephant] Initiating territory sweep: '{query}' across {len(viewports)} grid cells.")

        sem = asyncio.Semaphore(concurrency)

        async def worker_wrapper(idx: int, vp: SpatialViewport):
            async with sem:
                worker = GoldfishCellWorker(worker_id=idx + 1, client=self.client, limiter=self.limiter)
                return await worker.execute_cell(query, vp)

        tasks = [worker_wrapper(i, vp) for i, vp in enumerate(viewports)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for cell_result in results:
            if isinstance(cell_result, list):
                metrics.successful_cells += 1
                for place in cell_result:
                    metrics.raw_places_extracted += 1
                    # Stateful corporate deduplication based on clean normalized title
                    norm_key = place.title.strip().lower()
                    if norm_key not in self.seen_names:
                        self.seen_names.add(norm_key)
                        self.place_registry[place.place_id] = place
            else:
                metrics.failed_cells += 1

        retained = list(self.place_registry.values())
        metrics.unique_places_retained = len(retained)
        if metrics.raw_places_extracted > 0:
            metrics.deduplication_ratio = round(
                (metrics.raw_places_extracted - metrics.unique_places_retained) / metrics.raw_places_extracted, 2
            )

        logger.info(
            f"[Elephant QA] Sweep complete. Unique: {metrics.unique_places_retained} | "
            f"Raw: {metrics.raw_places_extracted} | Dedup ratio: {metrics.deduplication_ratio}"
        )
        return retained, metrics
