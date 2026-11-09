"""Spatial bounding box decomposition and geo-grid partitioning."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List
from atlas_maps.core.wire import SpatialViewport


@dataclass(frozen=True)
class BoundingBox:
    """Geographic bounding box defined by south-west and north-east corners."""
    min_lat: float
    min_lng: float
    max_lat: float
    max_lng: float

    def partition(self, rows: int = 2, cols: int = 2) -> List[SpatialViewport]:
        """
        Subdivide bounding box into a grid matrix of viewports.
        Ensures high resolution search coverage across dense urban territories.
        """
        lat_step = (self.max_lat - self.min_lat) / rows
        lng_step = (self.max_lng - self.min_lng) / cols
        
        viewports: List[SpatialViewport] = []
        for r in range(rows):
            for c in range(cols):
                center_lat = self.min_lat + (r + 0.5) * lat_step
                center_lng = self.min_lng + (c + 0.5) * lng_step
                # Calculate zoom based on span
                zoom = 15 if max(lat_step, lng_step) < 0.05 else 13
                viewports.append(
                    SpatialViewport(
                        center_lat=round(center_lat, 6),
                        center_lng=round(center_lng, 6),
                        zoom_level=zoom,
                        span_lat=round(lat_step, 6),
                        span_lng=round(lng_step, 6),
                    )
                )
        return viewports


# Pre-configured metropolitan presets for instant intelligence querying
METROPOLITAN_PRESETS = {
    "london_central": BoundingBox(min_lat=51.4800, min_lng=-0.1800, max_lat=51.5300, max_lng=-0.0800),
    "manhattan": BoundingBox(min_lat=40.7000, min_lng=-74.0200, max_lat=40.8000, max_lng=-73.9300),
    "san_francisco": BoundingBox(min_lat=37.7400, min_lng=-122.5000, max_lat=37.8100, max_lng=-122.3800),
    "dubai_marina_downtown": BoundingBox(min_lat=25.0700, min_lng=55.1300, max_lat=25.2100, max_lng=55.2900),
    "tokyo_central": BoundingBox(min_lat=35.6500, min_lng=139.6800, max_lat=35.7200, max_lng=139.7800),
}
