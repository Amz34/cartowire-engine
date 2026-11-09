"""Strongly-typed corporate Pydantic models for spatial and place data."""
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


class GeoCoordinates(BaseModel):
    """Geographic WGS84 coordinate pair."""
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)


class PlaceReview(BaseModel):
    """Individual client review extract."""
    author_name: str
    rating: float = Field(..., ge=1.0, le=5.0)
    relative_time: str
    text: Optional[str] = None


class PlaceMetadata(BaseModel):
    """Normalized commercial place record."""
    place_id: str = Field(..., description="Unique Google Maps place identifier")
    title: str = Field(..., description="Business or place display title")
    category: Optional[str] = Field(None, description="Primary business taxonomy")
    address: Optional[str] = Field(None, description="Formatted full address")
    phone: Optional[str] = Field(None, description="E.164 or formatted local contact number")
    website: Optional[str] = Field(None, description="Verified domain or link")
    rating: Optional[float] = Field(None, ge=0.0, le=5.0, description="Aggregated rating score")
    review_count: Optional[int] = Field(None, ge=0, description="Total verified review volume")
    coordinates: Optional[GeoCoordinates] = None
    cid: Optional[str] = Field(None, description="Google Customer Identification number")


class SearchResultSet(BaseModel):
    """Collection wrapper for batch execution results."""
    query: str
    total_extracted: int
    results: List[PlaceMetadata] = Field(default_factory=list)
