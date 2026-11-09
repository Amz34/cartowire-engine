# Atlas Maps Engine

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-Enabled-green.svg)](https://modelcontextprotocol.io)

High-performance wire-level Google Maps discovery engine, CLI, and Model Context Protocol (MCP) server.

Unlike conventional scrapers that rely on fragile DOM traversal, **Atlas Maps Engine** interacts directly with internal spatial wire endpoints and serialized application state buffers (`APP_INITIALIZATION_STATE`), drastically reducing latency and operational overhead.

---

## Key Features

- **Wire-Level Extraction:** Extracts clean positional records directly from server-hydrated application state without fragile DOM selectors.
- **Restriction Resilience:** Built-in TLS fingerprint impersonation (JA3/JA4 Chrome profiles via `curl-cffi`) and exponential backoff retry policies.
- **Model Context Protocol (MCP):** Native integration allowing AI agents (Claude, Cursor, Copilot) to query geographic and commercial points of interest directly.
- **Typed Data Layer:** Strict validation using Pydantic v2 ensuring verified coordinates, ratings, and contact records.

---

## Architecture Overview

```
[ User Query / MCP Tool Call ]
              │
              ▼
   [ Spatial Wire Encoder ] ──── (Generates !1m... protobuf tokens & viewports)
              │
              ▼
  [ TLS Impersonation Transport ] ── (curl-cffi Chrome 120 client hello)
              │
              ▼
   [ Stream State Parser ] ────── (Parses APP_INITIALIZATION_STATE array)
              │
              ▼
    [ Pydantic Models ] ──────── (Verified PlaceMetadata records)
```

---

## Installation

```bash
pip install atlas-maps-engine
```

For development installations:

```bash
git clone https://github.com/your-org/atlas-maps-engine.git
cd atlas-maps-engine
pip install -e ".[dev]"
```

---

## Quick Start

### 1. Command Line Interface (CLI)

Search for commercial venues or points of interest:

```bash
atlas-maps "Specialty Coffee Brooklyn"
```

Output with structured JSON serialization:

```bash
atlas-maps "Boutique Hotels Tokyo" --lat 35.6762 --lng 139.6503 --json
```

### 2. Python API

```python
from atlas_maps import MapsClient, SpatialViewport, build_search_url
from atlas_maps.core.parsers import extract_initialization_state, parse_place_entries

# 1. Build spatial URL
viewport = SpatialViewport(center_lat=40.7128, center_lng=-74.0060, zoom_level=14)
url = build_search_url("Fintech Accelerators Manhattan", viewport)

# 2. Fetch using TLS impersonation transport
client = MapsClient()
html = client.fetch_page(url)

# 3. Parse serialized array state
state = extract_initialization_state(html)
places = parse_place_entries(state)

for place in places:
    print(f"{place.title} | Rating: {place.rating} ({place.review_count} reviews)")
```

### 3. Model Context Protocol (MCP) Server

Run the MCP server to connect directly with Claude Desktop or Cursor:

```bash
python -m atlas_maps.mcp.server
```

Configuration for Claude Desktop (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "atlas-maps": {
      "command": "python",
      "args": ["-m", "atlas_maps.mcp.server"]
    }
  }
}
```

---

## Testing

Execute the test suite verifying spatial Protobuf generation and crash-proof parsing:

```bash
pytest tests/
```

---

## License

This project is licensed under the Apache 2.0 License.
