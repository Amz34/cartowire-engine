"""Wire protocol definitions and spatial protobuf encoders for Google Maps queries."""
from __future__ import annotations

import base64
import urllib.parse
from dataclasses import dataclass
from typing import Optional


def encode_varint(value: int) -> bytes:
    """Encode an integer as a standard Protobuf varint."""
    bits = value & 0x7F
    value >>= 7
    ret = bytearray()
    while value:
        ret.append(0x80 | bits)
        bits = value & 0x7F
        value >>= 7
    ret.append(bits)
    return bytes(ret)


def encode_tag(field_num: int, wire_type: int) -> bytes:
    """Encode protobuf tag."""
    return encode_varint((field_num << 3) | wire_type)


def encode_string(field_num: int, val: str) -> bytes:
    """Encode length-delimited string."""
    b = val.encode("utf-8")
    return encode_tag(field_num, 2) + encode_varint(len(b)) + b


def encode_bytes(field_num: int, val: bytes) -> bytes:
    """Encode length-delimited bytes."""
    return encode_tag(field_num, 2) + encode_varint(len(val)) + val


def encode_int(field_num: int, val: int) -> bytes:
    """Encode varint field."""
    return encode_tag(field_num, 0) + encode_varint(val)


@dataclass(frozen=True)
class SpatialViewport:
    """Represents a bounding geographic bounding box and center coordinates."""
    center_lat: float
    center_lng: float
    zoom_level: int = 14
    span_lat: float = 0.05
    span_lng: float = 0.05

    def to_pb_path(self) -> str:
        """
        Build Google's internal spatial proto segment for URL routing:
        !1m4!1m3!1d{zoom}!2d{lng}!3d{lat}
        """
        lat_fixed = f"{self.center_lat:.7f}"
        lng_fixed = f"{self.center_lng:.7f}"
        return f"!1m4!1m3!1d{self.zoom_level}!2d{lng_fixed}!3d{lat_fixed}"


def build_search_url(
    query: str,
    viewport: Optional[SpatialViewport] = None,
    language: str = "en",
    hl: str = "en",
) -> str:
    """
    Construct a clean, restriction-resistant Google Maps RPC URL.
    Bypasses fragile front-end DOM routing.
    """
    base_url = "https://www.google.com/maps/search/"
    encoded_query = urllib.parse.quote_plus(query)
    
    if viewport:
        return f"{base_url}{encoded_query}/@{viewport.center_lat:.7f},{viewport.center_lng:.7f},{viewport.zoom_level}z?hl={hl}&gl=us"
    
    return f"{base_url}{encoded_query}?hl={hl}&gl=us"
