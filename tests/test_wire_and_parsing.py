"""Test suite for wire protocol and state parsing validation."""
import pytest
from atlas_maps.core.wire import SpatialViewport, build_search_url
from atlas_maps.core.parsers import extract_initialization_state, parse_place_entries


def test_spatial_viewport_pb_generation():
    vp = SpatialViewport(center_lat=51.5074, center_lng=-0.1278, zoom_level=14)
    path = vp.to_pb_path()
    assert "!1d14" in path
    assert "!2d-0.1278000" in path
    assert "!3d51.5074000" in path


def test_build_search_url_formatting():
    url = build_search_url("Tech Companies Austin")
    assert "google.com/maps/search/Tech+Companies+Austin" in url
    assert "hl=en" in url


def test_state_parser_safeguards():
    # Verify no crash on empty or irregular blobs
    res = parse_place_entries([])
    assert res == []

    # Verify extraction from mock initialization state
    mock_html = """
    <html>
      <script>
        window.APP_INITIALIZATION_STATE = [[], [], [], [[[], [], ["id1", null, null, null, [null, null, null, null, null, null, null, 4.8, 120], null, null, null, null, [null, null, 37.7749, -122.4194], "pid_123", "Apex AI Labs", null, ["Software Company"]]]]];
      </script>
    </html>
    """
    state = extract_initialization_state(mock_html)
    assert state is not None
    places = parse_place_entries(state)
    assert len(places) == 1
    assert places[0].title == "Apex AI Labs"
    assert places[0].rating == 4.8
    assert places[0].review_count == 120
    assert places[0].category == "Software Company"
