# Atlas Maps Engine - Technical Architecture Specification

## 1. System Topology

```
                       [ Incoming Client / CLI / FastMCP Tool ]
                                          │
                                          ▼
                               [ Elephant Coordinator ]
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  ▼                                               ▼
         [ Spatial Grid Decomposer ]                     [ Token Bucket Limiter ]
                  │                                               │
                  └───────────────────────┬───────────────────────┘
                                          ▼
                              [ Goldfish Worker Swarm ]
                                          │
                     ┌────────────────────┴────────────────────┐
                     ▼                                         ▼
         [ Fast HTTP / TLS Transport ]             [ Headless Chromium Engine ]
          (curl-cffi Chrome120 JA3)                 (Playwright /usr/bin/google-chrome)
                     │                                         │
                     └────────────────────┬────────────────────┘
                                          ▼
                             [ Stream Array Decoders ]
                            (APP_INITIALIZATION_STATE)
                                          │
                                          ▼
                         [ Stateful Entity Deduplicator ]
                                          │
                                          ▼
                            [ Typed Pydantic v2 Models ]
```

## 2. Core Operational Primitives

### 2.1 Spatial Protobuf Construction
Google Maps resolves spatial views using compact Protobuf tokens embedded in the path component:
- `!1m4`: Message wrapper with 4 sub-elements
- `!1m3`: Viewport configuration
- `!1d{zoom}`: Float or integer zoom altitude
- `!2d{lng}`: Fixed-precision decimal longitude
- `!3d{lat}`: Fixed-precision decimal latitude

### 2.2 Dual-Layer Resilience Mechanism
To maintain operational continuity under strict anti-scraping scrutiny:
1. **Direct TLS Impersonation:** Requests mimic Chrome 120 client hello cipher suites, elliptic curves, and HTTP/2 framing.
2. **Headless Failover:** On mitigation challenges, queries transition automatically to a headless Chromium instance executing with sandbox and GPU overrides.

### 2.3 Elephant-Goldfish Model (EGM)
- **The Elephant:** Retains long-term state across the sweep, preventing duplicate entity emission and balancing request velocity.
- **Goldfish Workers:** Ephemeral workers spawned per grid tile, decoupling session state and preventing memory fragmentation.
