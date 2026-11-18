from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from pathsnap.route_geometry import arcs_to_segments, collapse_arc_sequence  # noqa: E402

NODES = np.array([[10.0, 50.0], [10.1, 50.0], [10.2, 50.0], [20.0, 60.0], [20.1, 60.0]])  # lon, lat
ARCS = np.array([(0, 1), (1, 2), (3, 4)])


def test_collapse_removes_repeats_and_missing():
    assert collapse_arc_sequence(np.array([0, 0, -1, 1, 1, 2])) == [0, 1, 2]


def test_connected_arcs_form_one_segment_in_lat_lon_order():
    segments = arcs_to_segments([0, 1], ARCS, NODES)
    assert segments == [[[50.0, 10.0], [50.0, 10.1], [50.0, 10.2]]]


def test_disconnected_jump_starts_new_segment():
    segments = arcs_to_segments([0, 2], ARCS, NODES)
    assert len(segments) == 2 and segments[1][0] == [60.0, 20.0]


def test_empty_sequence():
    assert arcs_to_segments([], ARCS, NODES) == []
